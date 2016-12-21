#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import os

try:
    from termcolor import cprint
except ImportError:
    def cprint(string, *args, **kwargs):
        print(string)

from . import logfile
from . import xmlfile


def main(options):
    xmlfile.main(options)
    logfile.main(options)


def print_progress(filename):
    cprint('=== {} ==='.format(filename), 'white')
