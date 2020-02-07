#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <martin-ueding.de>

import os

try:
    from termcolor import cprint
except ImportError:
    def cprint(string, *args, **kwargs):
        print(string)

from . import logfile
from . import xmlfile
import wflow


def main(options):
    for dirname in options.dirname:
        wflow.process_directory(dirname)
    xmlfile.main(options)
    logfile.main(options)


def print_progress(filename):
    cprint('=== {} ==='.format(filename), 'white')
