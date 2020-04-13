"""Command-line interface for exporteer_evernote_osx tool."""


import argparse
import sys
from exporteer_evernote_osx import enapp


def _notebooks(args):
    for name in enapp.list_notebooks():
        print(name)
    return 0


def _sync(args):
    enapp.start_sync()
    if args.immediate:
        return 0

    try:
        enapp.await_sync(timeout_seconds=args.timeout, delay_seconds=args.delay)
    except enapp.SyncTimeoutException:
        print('timed out waiting for Evernote app to sync', file=sys.stderr)
        return 2

    return 0


def main(args=None):
    """Runs the tool and returns its exit code.

    args may be an array of string command-line arguments; if absent,
    the process's arguments are used.
    """
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    subs = parser.add_subparsers(title='Commands')

    p_notebooks = subs.add_parser(
        'notebooks',
        help='list notebooks')
    p_notebooks.set_defaults(func=_notebooks)

    p_sync = subs.add_parser(
        'sync',
        help='tell app to synchronize and wait for it to finish')
    p_sync.add_argument(
        '-d', '--delay', nargs=1, type=int,
        help='seconds to wait between each poll (default 10)')
    p_sync.add_argument(
        '-i', '--immediate', action='store_true',
        help='return immediately without waiting for sync to finish')
    p_sync.add_argument(
        '-t', '--timeout', nargs=1, type=int,
        help='seconds to wait before failing (default 1800 = 30 min)')
    p_sync.set_defaults(func=_sync)

    args = parser.parse_args(args)
    if not args.func:
        parser.print_help()
        return 1
    return args.func(args)
