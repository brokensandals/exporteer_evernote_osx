"""Allows interacting with the Evernote OSX app."""

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
    export (find notes "$query") to (POSIX file "$dest") format $fmt
end tell
""")

# This is a very hacky/incomplete way of parsing AppleScript results,
# and would give wrong results for notebook names containing quotation
# marks.
_NOTEBOOK_NAMES_RE = re.compile('"(.+?)"')


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


def export(dest, fmt='HTML', query=''):
    """Exports notes.

    This method will raise an error if there are no matching notes.

    fmt should be HTML or ENEX.
    dest should be a string path name. For fmt=HTML it should be the
    target dir; for fmt=ENEX it should be the target file. The dest
    does not need to exist yet.

    query is the Evernote search query for choosing which notes to export.
    It defaults to an empty string, which should match all notes.
    """
    dest_esc = _script_escape(dest)
    query_esc = _script_escape(query)
    script = _EXPORT_SCRIPT.substitute({
        'dest': dest_esc,
        'fmt': fmt,
        'query': query_esc,
    })
    subprocess.check_call(['osascript', '-e', script])
