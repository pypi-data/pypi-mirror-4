#!/usr/bin/env python
# coding: utf-8

from setuptools import setup


setup(
    name='json_tools',
    version='0.2.0',

    packages=['json_tools'],
    package_dir={'json_tools': 'lib'},
    install_requires=['colorama'],

    entry_points={
        'console_scripts': [
            'json = json_tools.__main__:main',
        ]
    },

    author='Vadim Semenov',
    author_email='protoss.player@gmail.com',
    url='https://bitbucket.org/vadim_semenov/json_tools',

    description='A set of tools to manipulate JSON: diff, patch, pretty-printing',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    long_description="""
    json_tools is a Python package and CLI utility set to manipulate JSON documents
    using JSON patch specification: <http://tools.ietf.org/html/draft-ietf-appsawg-json-patch-02>

    Installation
    ============
    ``pip install json_tools``

    Usage (CLI)
    ===========

    Pretty-printing
    ---------------
    ``json print [options] [file_name]``

    The ``file_name`` is optional: if not given the input document is read from STDIN.

    Options
    ^^^^^^^
    ``-c, --color``
        Colorize output (used only in TTY mode).


    Diff
    ----
    ``json diff first.json second.json``

    Patch
    -----
    ``json patch document.json patch.json``


    Source code
    ===========

    Source code and Wiki are available on BitBucket: <https://bitbucket.org/vadim_semenov/json_tools>
    Feel free to fork and make bug-reports/feature-requests.
    """
)
