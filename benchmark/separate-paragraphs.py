#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <martin-ueding.de>

import argparse


def main():
    options = _parse_args()

    for filename in options.file:
        paragraphs = []
        with open(filename) as f:
            cur_par = []
            for line in f:
                if len(line.strip()) == 0:
                    paragraphs.append(cur_par)
                    cur_par = []
                else:
                    cur_par.append(line)

        for i, par in enumerate(paragraphs):
            with open('{}-{:04d}.txt'.format(filename, i), 'w') as f:
                f.write(''.join(par))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('file', nargs='+')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
