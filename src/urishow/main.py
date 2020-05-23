#!/usr/bin/env python3

import argparse
import re
import os
import sys
import tui


def _launch(uri, cmd=None):
    """
    Launch the uri with the correct command.
    """
    if cmd is None:
        if re.match(r'mailto:', uri) and os.environ.get('MAIL') is not None:
            cmd = os.environ.get('MAIL')
        else:
            cmd = os.environ.get('BROWSER')
    os.system("{} '{}' 2> /dev/null".format(cmd, uri))


def _extract(text, regex=None):
    """
    Extract all the uris from the given text.
    """
    if regex is None:
        regex = r'((https?|mailto):(//)?[^ <>"\t]*|(www)[0-9]?\.[-a-z0-9.]+)[^ .,;\t\n\r<">\):]?[^, <>"\t]*[^ .,;\t\n\r<">\):]'
        return [match[0] for match in re.findall(regex, text)]
    else:
        return re.findall(regex, text)


def _read(fd):
    """
    Read the contents of the given file descriptor and free up the sys.stdin so
    ncurses keyboard input is not blocked.
    """
    text = fd.read()
    if not os.isatty(0):
        fd = os.open('/dev/tty', os.O_RDONLY)
        if fd < 0:
            sys.stderr.write('Unable to open an input tty.\n')
            sys.exit(-1)
        else:
            os.dup2(fd, 0)
            os.close(fd)
    return text


def _getopts():
    """
    Read and process the commandline arguments.
    """
    desc = 'Extract, show, select and launch uri\'s.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument('-p', action='store_false', help='just print the extracted uri\'s')
    parser.add_argument('-r', metavar='REGEX',   help='regex for extracting uri\'s')
    parser.add_argument('-c', metavar='COMMAND', help='command to launch uri')
    parser.add_argument('-f', metavar='FILE',    help='file to extract uri\'s from',
                        type=argparse.FileType('r'), default=sys.stdin)

    args = vars(parser.parse_args())
    return args['r'], args['c'], args['f'], args['p']


def main():
    regex, cmd, fd, ask = _getopts()
    text = _read(fd)
    uris = _extract(text, regex)
    if not ask:
        for uri in uris:
            print(uri)
    elif len(uris) == 0:
        print("No uri was found.")
    else:
        uri  = tui.show(uris)
        if uri is not None:
            _launch(uri, cmd)


if __name__ == '__main__':
    main()
