#!/usr/bin/env python
# encoding: utf-8

""" CLI tool entry point.
"""

from __future__ import print_function

import json
import sys
from optparse import OptionParser

import json_tools
from print_style import colorize


def usage():
    _CMDS = {'print': 'Pretty-print a JSON file',
             'diff': 'Diff between two JSON documents',
             'patch': 'Patch a JSON document',
            }
    print("Usage:", sys.argv[0], " <cmd> [options]")
    print("\nAvailable commands:")
    for cmd, info in _CMDS.items():
        print("  ", colorize(cmd, bold=True), "\t", info)


def pretty_print():
    parser = OptionParser()
    parser.add_option("-c", "--color", dest="colors", action="store_true",
                      help="Colorize the output", default=False)
    options, files = parser.parse_args()
    file_name = files[0] if files else '/dev/stdin'

    try:
        f = open(file_name)
    except:
        print("Could not open input file", file=sys.stderr)
        exit(-1)

    try:
        data = json.load(f)
    except IOError:
        print("Could not decode JSON from the input file", file=sys.stderr)
        exit(-1)
    json_tools.print_json(data, options.colors)


def diff():
    parser = OptionParser()
    parser.add_option("-c", "--color", dest="colors", action="store_true",
                      help="Colorize the output", default=False)
    options, files = parser.parse_args()
    if len(files) < 2:
        print("Need at least 2 JSON files", file=sys.stderr)
        exit(-1)

    try:
        with open(files[0]) as f:
            local = json.load(f)
    except IOError:
        print('Local not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to file not specified', file=sys.stderr)
        exit(-1)

    try:
        with open(files[1]) as f:
            other = json.load(f)
    except IOError:
        print('Other not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to other file not specified', file=sys.stderr)
        exit(-1)

    res = json_tools.diff(local, other)
    json_tools.print_json(res, options.colors)


def patch():
    parser = OptionParser()
    parser.add_option("-c", "--color", dest="colors", action="store_true",
                      help="Colorize the output", default=False)
    options, files = parser.parse_args()
    if len(files) == 1:
        source = '/dev/stdin'
        patch = files[0]
    elif len(files) >= 2:
        source, patch = files[0:2]
    else:
        print("Need at least 1 JSON files", file=sys.stderr)
        exit(-1)

    try:
        with open(source) as f:
            data = json.load(f)
    except IOError:
        print('Source file not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to file not specified', file=sys.stderr)
        exit(-1)

    try:
        with open(patch) as f:
            patch = json.load(f)
    except IOError:
        print('Patch not found', file=sys.stderr)
        exit(-1)
    except KeyError:
        print('Path to other file not specified', file=sys.stderr)
        exit(-1)

    res = json_tools.patch(data, patch)
    json_tools.print_json(res, options.colors)


COMMANDS = {
    'print': pretty_print,
    'diff': diff,
    'patch': patch
}


def main():
    if len(sys.argv) < 2:
        usage()
        exit(-1)
    else:
        cmd = sys.argv[1]
        sys.argv = sys.argv[1:]
        try:
            COMMANDS[cmd]()
        except KeyError:
            print('Bad command:', cmd, file=sys.stderr)
            exit(-1)


if __name__ == '__main__':
    main()
