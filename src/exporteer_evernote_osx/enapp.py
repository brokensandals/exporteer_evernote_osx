"""Allows interacting with the Evernote OSX app."""

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
