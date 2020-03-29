#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

import argparse


def main():
    options = _parse_args()

    for sc_in in range(6):
        for sc_out in range(6):
            if sc_out < sc_in:
                idx15 = sc_in * (sc_in - 1) // 2 + sc_out

                print('{:2d} {:2d} {:2d}'.format(sc_in, sc_out, idx15))
            else:
                idx15 = sc_out * (sc_out - 1) // 2 + sc_in

                print('{:2d} {:2d} {:2d}'.format(sc_in, sc_out, idx15))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
