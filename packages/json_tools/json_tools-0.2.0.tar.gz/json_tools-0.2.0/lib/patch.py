#!/usr/bin/env python
#-*- coding:utf-8 -*-


""" Functions to patch JSON documents.
"""

from __future__ import print_function

from json_tools.path import split


def add(data, path, value, replace=False):
    """ Add a new value to the given JSON document @a data at JSON-path @a path.

        If the the path is already used, then no changes are made.
    """

    nodes = split(path)
    pos = len(nodes)
    d = data
    for node in nodes:
        name = node['name']
        pos -= 1
        if node['t'] == 'object':
            if name not in d:
                d[name] = {}
            elif pos == 0 and not replace:
                break
        elif node['t'] == 'array':
            if name not in d:
                d[name] = []
            elif pos == 0 and not replace:
                break
        else:  # array-index
            if name < len(d) and pos == 0 and not replace:
                break
            for i in range(len(d), name):
                d.append(None)
            #d.append({})
        if pos == 0:
            d[name] = value
        else:
            d = d[name]
    return data


def replace(data, path, value):
    """ Replace the value of the document's subelement at @a path with value
        @a value.
    """
    return add(data, path, value, True)


def remove(data, path):
    nodes = split(path)
    pos = len(nodes)
    d = data
    for node in nodes:
        name = node['name']
        if node['t'] in ('object', 'array'):
            if name not in d:
                return
            else:
                pos -= 1
                if pos == 0:
                    del d[name]
                else:
                    d = d[name]
        else:  # array-index
            if name >= len(d):
                return
            else:
                pos -= 1
                if pos == 0:
                    del d[name]
                else:
                    d = d[name]
    return data


def patch(data, patch):
    """ Apply a JSON @a patch to the given JSON object @a data.
    """

    for change in patch:
        if 'add' in change:
            add(data, change['add'], change['value'])
        elif 'replace' in change:
            replace(data, change['replace'], change['value'])
        elif 'remove' in change:
            remove(data, change['remove'])
    return data


if __name__ == '__main__':
    import json
    from sys import argv, stderr
    from printer import print_json

    try:
        argv.remove('--pretty')
        pretty = True
    except ValueError:
        pretty = False

    if len(argv) < 3:
        print("Usage:", argv[0], "[options] path/to.json path/to.patch")
        exit(-1)

    try:
        with open(argv[1]) as f:
            data = json.load(f)
    except IOError:
        print('Local not found', file=stderr)
        exit(-1)

    try:
        with open(argv[2]) as f:
            _patch = json.load(f)
    except IOError:
        print('Patch not found', file=stderr)
        exit(-1)

    res = patch(data, _patch)
    print_json(res, pretty)
