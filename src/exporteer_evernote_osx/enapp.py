"""Allows interacting with the Evernote OSX app."""

import re
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
