#!/usr/bin/env python3

import argparse
import re
import sys
import tui


def _launch(uri, cmd=None):
    """
    Launch the uri with the correct command.
    """
    if cmd is not None:
        os.system()
    print('{} {}.'.format(cmd, uri))


def _extract(text, regex=None):
    """
    Extract all the uris from the given text.
    """
    return text.split('\n')


def _getopts():
    """
    Read and process the commandline arguments.
    """
    desc = 'Extract, show, select and launch uri\'s.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-r', metavar='REGEX',   help='regex for extracting uri\'s')
    parser.add_argument('-c', metavar='COMMAND', help='command to launch uri')
    parser.add_argument('-f', metavar='FILE',    help='file to extract uri\'s from',
                        type=argparse.FileType('r'), default=sys.stdin)

    args = vars(parser.parse_args())
    return args['r'], args['c'], args['f']


def main():
    regex, cmd, fd = _getopts()
    with fd:  # TODO Do not close the stdin.
        text = fd.read()
    uris = _extract(text, regex)
    uri  = tui.show(uris)
    if uri is not None:
        _launch(uri, cmd)


if __name__ == '__main__':
    main()
