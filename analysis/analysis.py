#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import os

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

import extractors
import visualizers
import wflow


def main(options):
    pass


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.set_defaults(func=main)
    subparsers = parser.add_subparsers()

    parser_extract = subparsers.add_parser('extract')
    parser_extract.set_defaults(func=extractors.main)
    parser_extract.add_argument('dirname', nargs='+')

    parser_visualize = subparsers.add_parser('visualize')
    parser_visualize.set_defaults(func=visualizers.main)
    parser_visualize.add_argument('dirname', nargs='+')
    parser_visualize.add_argument('--shift', action='store_true', help='Shift the X values for better legibility')
    parser_visualize.add_argument('--shift-amount', type=float, default=0.1, help='Shift per curve (default: %(default)s)')
    parser_visualize.add_argument('--united-name', default='plots.pdf', help='Filename for combined PDF of all plots (default: %(default)s)')

    parser_wflow = subparsers.add_parser('wflow')
    parser_wflow.set_defaults(func=wflow.main)
    parser_wflow.add_argument('xml', nargs='+')

    options = parser.parse_args()
    options.func(options)


if __name__ == '__main__':
    _parse_args()
