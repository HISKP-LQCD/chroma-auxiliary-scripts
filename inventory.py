#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import itertools
import os
import re


regex_cfg = r'_cfg_(\d+)\.lime'
regex_wflow = r'wflow.config-(\d+)\.out\.xml'
regex_stout = r'stout.config-(\d+)\.lime'
regex_eigenvalues = r'eigenvalues.(\d+).095'


Ensemble = collections.namedtuple('Ensemble', ('name', 'gauges', 'stout', 'eigenvalues'))


def main():
    options = _parse_args()

    ensembles = [
        Ensemble(
            'L = 24 Forward Replica',
            ('/work/hbn28/hbn28e/0120-Mpi270-L24-T96/cfg',),
            ('/work/hbn28/hbn28e/0120-Mpi270-L24-T96/stout',),
            ('/work/hbn28/hbn284/eigensystems/0120-Mpi270-L24-T96',),
        ),
        Ensemble(
            'L = 24 Backward Replica',
            ('/work/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/cfg',),
            ('/work/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/stout',),
            ('/work/hbn28/hbn284/eigensystems/0122-Mpi270-L24-T96-backwards',),
        ),
        Ensemble(
            'L = 32 Forward Replica',
            ('/work/hbn28/hbn28e/0121-Mpi270-L32-T96/cfg',),
            ('/work/hbn28/hbn28e/0121-Mpi270-L32-T96/stout',),
            ('/work/hbn28/hbn284/eigensystems/0121-Mpi270-L32-T96',),
        ),
        Ensemble(
            'L = 32 Backward Replica',
            ('/work/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/cfg',),
            ('/work/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/stout',),
            ('/work/hbn28/hbn284/eigensystems/0123-Mpi270-L32-T96-backwards',),
        ),
    ]

    for ensemble in ensembles:
        do_ensemble(ensemble)


def do_ensemble(ensemble):
    print(ensemble.name)

    do_type('Gauge (Raw)', ensemble.gauges, regex_cfg)
    do_type('Gauge (Stout)', ensemble.stout, regex_stout)
    do_type('Eigenvalues', ensemble.eigenvalues, regex_eigenvalues)
    print()


def do_type(name, directories, regex):

    for directory in directories:
        if not os.path.isdir(directory):
            continue

        files = os.listdir(directory)

        matches = [re.search(regex, filename) for filename in files]
        numbers = sorted([int(m.group(1)) for m in matches if m])
        ranges = list(get_ranges(numbers))
        strides = list(get_strides(ranges))
        #print(name, ', '.join(['{}..{}'.format(*r) for r in ranges]))
        print('  {:15s} {}'.format(name, ', '.join([format_stride(r) for r in strides])))


def format_stride(stride):
    lower, upper, step = stride
    if step == 1:
        return '{}..{}'.format(lower, upper)
    else:
        return '{}..{}..{}'.format(lower, upper, step)


def get_ranges(i):
    '''
    http://stackoverflow.com/a/4629241
    '''
    for a, b in itertools.groupby(enumerate(i), lambda x: x[1] - x[0]):
        b = list(b)
        yield b[0][1], b[-1][1]


def get_strides(ranges):
    for length, groups in itertools.groupby(ranges, lambda x: x[1] - x[0]):
        groups = list(groups)
        if length != 0:
            for a, b in groups:
                yield a, b, 1
        else:
            for offset, rgs in itertools.groupby(zip(groups[1:], groups[:-1]), lambda x: x[0][0] - x[1][0]):
                rgs = list(rgs)
                yield rgs[0][1][0], rgs[-1][0][0], offset




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
