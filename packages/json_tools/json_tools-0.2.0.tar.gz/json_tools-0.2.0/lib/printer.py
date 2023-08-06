#!/usr/bin/env python
#-*- coding:utf-8 -*-


""" Pretty-printing facility for JSON.
"""


from __future__ import print_function

import json

from print_style import colorize


def print_json(data, pretty=False, tab_size=4):
    """ Prints JSON in a fancy colorized maner.
    """

    def _apply_style(text, *args, **kwargs):
        if pretty:
            return colorize(text, *args, **kwargs)
        else:
            return text

    LBRACE = _apply_style('{', 'blue')
    RBRACE = _apply_style('}', 'blue')
    LSQ = _apply_style('[', 'blue')
    RSQ = _apply_style(']', 'blue')

    def _recursive_print(chunk, indent=0, needs_comma=True, context=None):
        """ Recursively pretty-prints a single JSON atom (@a chunk).
        """
        if isinstance(chunk, dict):
            print(' ' * indent if context == 'array' else '', LBRACE, sep='')
            l = len(chunk)
            for i, (k, v) in enumerate(chunk.iteritems(), 1):
                print(' ' * (indent + tab_size), '"',
                      _apply_style(k, 'yellow', bold=True), sep='', end='": ')
                _recursive_print(v, indent + tab_size, i < l)
            print(' ' * indent, RBRACE, ',' if needs_comma else '', sep='')
        elif isinstance(chunk, list):
            print(' ' * indent if context == 'array' else '', LSQ, sep='')
            l = len(chunk)
            for i, item in enumerate(chunk, 1):
                _recursive_print(item, indent + tab_size, i < l, 'array')
            print(' ' * indent, RSQ, ',' if needs_comma else '', sep='')
        else:
            if context == 'array':
                print(' ' * indent, end='')

            view = json.dumps(chunk)
            if isinstance(chunk, int):
                view = _apply_style(view, 'red')
            elif isinstance(chunk, float):
                view = _apply_style(view, 'red')
            elif isinstance(chunk, basestring):
                view = _apply_style(view, 'green')
            print(view, ',' if needs_comma else '', sep='')

    _recursive_print(data, needs_comma=False)


if __name__ == '__main__':
    from sys import argv, stdin, stderr

    try:
        argv.remove('--pretty')
        pretty = True
    except ValueError:
        pretty = False

    if len(argv) == 2:
        source = open(argv[1])
    else:
        source = stdin

    try:
        doc = json.load(source)
    except:
        print("Bad input", file=stderr)

    print_json(doc, pretty)
