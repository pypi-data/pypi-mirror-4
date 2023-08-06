#!/usr/bin/env python
#-*- coding:utf-8 -*-


""" JSON paths manipulation utilities: splitting, etc.
"""


def split(path):
    result = []
    for node in path.split('/')[1:]:
        try:
            index = int(node)
        except ValueError:
            result.append({'t': 'object', 'name': node})
        else:
            if not len(result):
                # path starts with an integer, e.g. "/1/foo/bar". The
                # root-level object is an array. We don't support this (yet).
                raise NotImplementedError('json_tools does not (yet) support '
                                          'arrays at the root level.')
            result[len(result) - 1]['t'] = 'array'
            result.append({'t': 'index', 'name': index})

    return result
