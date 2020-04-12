"""Command-line interface for exporteer_todoist tool."""


import argparse


def main(args=None):
    """Runs the tool and returns its exit code.

    args may be an array of string command-line arguments; if absent,
    the process's arguments are used.
    """
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=None)

    subs = parser.add_subparsers(title='Commands')

    

    args = parser.parse_args(args)
    if not args.func:
        parser.print_help()
        return 1
    return args.func(args)
