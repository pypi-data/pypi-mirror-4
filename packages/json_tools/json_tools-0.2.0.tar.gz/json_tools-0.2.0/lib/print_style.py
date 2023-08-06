#!/usr/bin/env python
# coding: utf-8


""" Pretty-printing facility for CLI output. The module provides several
    functions each mapping output style to the semantics of JSON diff.

    Relies on 'colorama' package by Jonathan Hartley.
"""

import os
import sys

import colorama

colorama.init()

_RESET = colorama.Fore.RESET
_BOLD_S = colorama.Style.BRIGHT
_BOLD_E = colorama.Style.NORMAL
_STYLES = {
    'white': colorama.Fore.WHITE,
    'green': colorama.Fore.GREEN,
    'red': colorama.Fore.RED,
    'yellow': colorama.Fore.YELLOW,
    'blue': colorama.Fore.BLUE,
}


try:
    USE_COLORS = os.isatty(sys.stdout.fileno())
except AttributeError:
    # If sys.stdout is a StringIO instance it will not have a fileno attribute
    USE_COLORS = False


def colorize(text, color='white', bold=False):
    """ Applies the specified @a style to the arbitrary @a text.
    """
    if not USE_COLORS:
        return text
    elif not bold:
        return ''.join([_STYLES[color], text, _RESET])
    else:
        return ''.join([_BOLD_S, _STYLES[color], text, _RESET, _BOLD_E])
