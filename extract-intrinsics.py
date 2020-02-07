#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <martin-ueding.de>
# Licensed under the MIT license.

import argparse
import re


def main():
    options = _parse_args()

    pattern = re.compile(r'(_mm512_[^(]+)')

    matches = set()

    for filename in options.filename:
        print('Processing', filename)
        with open(filename) as f:
            for line in f:
                m = pattern.findall(line)
                for elem in m:
                    matches.add(elem)

    for elem in sorted(matches):
        print('- `{}`'.format(elem))



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
