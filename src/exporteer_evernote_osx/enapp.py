"""Allows interacting with the Evernote OSX app."""

from pathlib import Path
import re
from string import Template
import subprocess
import time


_START_SYNC_SCRIPT = """
tell application "Evernote"
    synchronize
end tell 
"""

_CHECK_SYNC_SCRIPT = """
tell application "Evernote"
    isSynchronizing
end tell
"""

_LIST_NOTEBOOKS_SCRIPT = """
tell application "Evernote"
    name of notebooks
end tell
"""

_EXPORT_SCRIPT = Template("""
tell application "Evernote"
    with timeout of $timeout seconds
        set results to (find notes "$query")
        if (count of results) > 0 then
            export (find notes "$query") to (POSIX file "$dest") format $fmt
            true
        else
            false
        end if
    end timeout
end tell
""")

_EXPORT_BY_NOTE_SCRIPT = Template("""
tell application "Evernote"
    with timeout of $timeout seconds
        set results to (find notes "$query")
        set metaList to {}
        set theNoteIndex to 1
        repeat with theNote in results
            set metaText to (name of notebook of theNote) & "~" & (note link of theNote)
            set metaList to metaList & {metaText}
            export {theNote} to (POSIX file ("$dest/" & theNoteIndex)) format $fmt
            set theNoteIndex to theNoteIndex + 1
        end repeat
        metaList
    end timeout
end tell
""")

# This is a very hacky/incomplete way of parsing AppleScript results,
# and would give wrong results for notebook names containing quotation
# marks.
_NOTEBOOK_NAMES_RE = re.compile('"(.+?)"')

# And this would give wrong results if you have quotes or tildes...
_EXTRA_META_RE = re.compile('"(.+?)~(.+?)"')


URL_META_RE = re.compile('<meta name="evernote-url" content="([^"]+)')


class SyncTimeoutException(Exception):
    pass


def start_sync():
    """Tells the Evernote app to start synchronizing."""
    subprocess.check_call(['osascript', '-e', _START_SYNC_SCRIPT])


def check_sync():
    """Returns True if the Evernote app is currently synchronizing."""
    out = subprocess.check_output(['osascript', '-e', _CHECK_SYNC_SCRIPT])
    return out.strip() == 'true'


def await_sync(timeout_seconds=60*30, delay_seconds=10):
    """If the Evernote app is synchronizing, waits for it to finish.

    This method will repeatedly poll app at an interval of delay_seconds.
    If synchronization has not finished before timeout_seconds elapses,
    SyncTimeoutException is raised.
    """
    start = time.time()
    while check_sync():
        if start + timeout_seconds < time.time():
            raise SyncTimeoutException(
                f'waited {timeout_seconds} seconds but sync did not finish')
        time.sleep(delay_seconds)


def list_notebooks():
    """Returns a list of notebook names.
    """
    out = subprocess.check_output(
        ['osascript', '-e', _LIST_NOTEBOOKS_SCRIPT, '-ss'])
    return _NOTEBOOK_NAMES_RE.findall(str(out, 'utf-8'))


def _script_escape(string):
    return string.replace('\\', '\\\\').replace('"', '\\"')


def export(dest, fmt='HTML', query='', timeout_seconds=30*60):
    """Exports notes. Returns False if no notes match the query.

    fmt should be HTML or ENEX.
    dest should be a string path name. For fmt=HTML it should be the
    target dir; for fmt=ENEX it should be the target file. The dest
    does not need to exist yet.

    query is the Evernote search query for choosing which notes to export.
    It defaults to an empty string, which should match all notes.

    If there are no matches, the method returns False and there may be
    no output files.
    """
    dest = Path(dest).resolve()
    dest_esc = _script_escape(str(dest))
    query_esc = _script_escape(query)
    script = _EXPORT_SCRIPT.substitute({
        'dest': dest_esc,
        'fmt': fmt,
        'query': query_esc,
        'timeout': timeout_seconds,
    })
    result = subprocess.check_output(['osascript', '-e', script, '-ss'])
    return str(result, 'utf-8').strip() == 'true'


def export_enhanced(dest, fmt='HTML', query='', timeout_seconds=30*60):
    """Exports notes with extra metadata.
    Only HTML format is supported.

    dest should be a string path name to the directory where the notes
    should be exported; it will be created if necessary.

    query is the Evernote search query for choosing which notes to export.
    It defaults to an empty string, which should match all notes.

    This method adds two nonstandard meta tags to each of the HTML files:
    "evernote-notebook" containing the notebook name, and "evernote-url"
    containing the note link (i.e. an evernote:// url).

    Furthermore, the appearance of any of the notes' note link in any of the
    notes' bodies is replaced by the filename of the exported note. This way,
    links between notes will work in the exported files, without access to Evernote.

    Returns False if no notes match the query.
    """
    if not fmt == 'HTML':
        raise ValueError('Enhanced export currently only supports HTML mode.')
    dest = Path(dest).resolve()
    tmp = dest.joinpath('tmp')
    tmp.mkdir(parents=True, exist_ok=True)
    tmp_esc = _script_escape(str(tmp))
    query_esc = _script_escape(query)
    script = _EXPORT_BY_NOTE_SCRIPT.substitute({
        'dest': tmp_esc,
        'fmt': fmt,
        'query': query_esc,
        'timeout': timeout_seconds,
    })
    out = subprocess.check_output(['osascript', '-e', script, '-ss'])
    metas = _EXTRA_META_RE.findall(str(out, 'utf-8'))
    if not metas:
        return False

    def available_path(name):
        prefix = 2
        candidate = dest.joinpath(name)
        while candidate.exists():
            candidate = dest.joinpath(f'{prefix}-{name}')
            prefix += 1
        return candidate

    path_metas = {}
    for path in tmp.glob('*/*.html'):
        newpath = available_path(path.name)
        respath = path.parent.joinpath(f'{path.name}.resources')
        path.rename(newpath)
        if respath.exists():
            respath.rename(newpath.with_name(f'{newpath.name}.resources'))
        path.parent.rmdir()

        index = int(path.parent.name)
        path_metas[newpath] = metas[index-1]
        _, link = metas[index-1]
    tmp.rmdir()

    for path in dest.glob('*.html'):
        text = path.read_text()
        notebook, link = path_metas[path]
        text = text.replace('<head>', f'<head><meta name="evernote-notebook" content="{notebook}"/><meta name="evernote-url" content="{link}"/>', 1)
        path.write_text(text)

    return True


def relink(folder):
    folder = Path(folder)
    link_paths = {}
    for path in folder.glob('**/*.html'):
        text = path.read_text()
        match = re.search(URL_META_RE, text)
        if match:
            link_paths[match.group(1)] = path.relative_to(folder)
    # This is extraordinarily inefficient, it would be much faster to
    # use a regex to find all links and then replace just the ones we found
    for path in folder.glob('**/*.html'):
        text = path.read_text()
        endhead = text.index('</head>')
        body = text[endhead:]
        for link, target in link_paths.items():
            body = body.replace(link, str(target))
        text = text[:endhead] + body
        path.write_text(text)


def export_by_notebook(dest, fmt='HTML', query='', timeout_seconds=30*60):
    """Exports notes into separate files/folders per notebook.

    This is like the export method, except dest should be a directory,
    which will be populated with a separate file or folder for each
    notebook for which there are notes matching the query.

    The query must not contain the string "notebook".

    The timeout is applied to each notebook, rather than the entire export.
    """
    if 'notebook' in query:
        # If two notebooks are specified in the search query, the results
        # will include notes from both. Raising an error is easier than
        # trying to parse/modify the query to make it work.
        raise Exception('query must not contain notebook')
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    for name in list_notebooks():
        nbdest = dest.joinpath(name)
        if fmt == 'ENEX':
            nbdest = nbdest.with_suffix('.enex')
        nbquery = f'notebook:"{name}" {query}'
        export(str(nbdest), fmt=fmt, query=nbquery,
               timeout_seconds=timeout_seconds)
