#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import datetime
import os


def main():
    options = _parse_args()

    bins = collections.defaultdict(lambda: 0)

    for filename in options.filename:
        mtime = os.path.getmtime(filename)
        dt = datetime.datetime.fromtimestamp(mtime)
        year, week, day_of_week = dt.isocalendar()
        key = '{:04d}-{:02d}'.format(year, week)

        bins[key] += 1

    for key, val in sorted(bins.items()):
        print('{}: {:4d}'.format(key, val))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('filename', nargs='+')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
