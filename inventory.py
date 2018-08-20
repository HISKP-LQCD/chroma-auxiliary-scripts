#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017-2018 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import glob
import itertools
import os
import re


regex_cfg = r'_cfg_(\d+)\.lime|conf\.(\d+)'
regex_stout = r'stout.config-(\d+)\.lime|conf\.(\d+)'
regex_wflow = r'wflow.config-(\d+)\.out\.xml'
regex_eigenvalues = r'eigenvalues.(\d+).095'
regex_eigenvectors = r'eigenvectors.(\d+).095'
regex_phases = r'phases.(\d+).095'


Ensemble = collections.namedtuple('Ensemble', ('name', 'gauges', 'stout', 'eigenvalues', 'perambulators'))


def main():
    options = _parse_args()

    ensembles = [
        Ensemble(
            'L = 16 Forward Replica',
            ('/work/hbn28/hbn28e/0106-Mpi660-L16-T32/cfg',
             '/arch2/hbn28/hbn28e/0106-Mpi660-L16-T32/cfg',),
            ('/work/hbn28/hbn28e/0106-Mpi660-L16-T32/stout',
             '/arch2/hbn28/hbn28e/0106-Mpi660-L16-T32/stout',
             '/hiskp2/gauges/0106-Mpi660-L16-T32/stout_smeared',),
            ('/work/hbn28/hbn284/eigensystems/0106-Mpi660-L16-T32',
             '/hiskp2/eigensystems/0106-Mpi660-L16-T32/hyp_062_062_3/nev_120'),
            ('/hiskp2/ueding/peram_generation/sWC_A2p1_Mpi660_L16T32',),
        ),
        Ensemble(
            'L = 24 Forward Replica',
            ('/work/hbn28/hbn28e/0120-Mpi270-L24-T96/cfg',
             '/arch2/hbn28/hbn28e/0120-Mpi270-L24-T96/cfg',),
            ('/work/hbn28/hbn28e/0120-Mpi270-L24-T96/stout',
             '/arch2/hbn28/hbn28e/0120-Mpi270-L24-T96/stout',
             '/hiskp2/gauges/0120-Mpi270-L24-T96/stout_smeared',),
            ('/work/hbn28/hbn284/eigensystems/0120-Mpi270-L24-T96',
             '/hiskp2/eigensystems/0120-Mpi270-L24-T96/hyp_062_062_3/nev_120'),
            ('/hiskp2/ueding/peram_generation/sWC_A2p1_Mpi270_L24T96',),
        ),
        Ensemble(
            'L = 24 Backward Replica',
            ('/work/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/cfg',
             '/arch2/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/cfg',),
            ('/work/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/stout',
             '/arch2/hbn28/hbn28e/0122-Mpi270-L24-T96-backwards/stout',
             '/hiskp2/gauges/sWC_A2p1_Mpi270_L24T96/backwards/stout'),
            ('/work/hbn28/hbn284/eigensystems/sWC_A2p1_Mpi270_L24T96_backwards',
             '/hiskp2/eigensystems/sWC_A2p1_Mpi270_L24T96_backwards'),
            ('/hiskp2/ueding/peram_generation/sWC_A2p1_Mpi270_L24T96_backwards',),
        ),
        Ensemble(
            'L = 32 Forward Replica',
            ('/work/hbn28/hbn28e/0121-Mpi270-L32-T96/cfg',
             '/arch2/hbn28/hbn28e/0121-Mpi270-L32-T96/cfg'),
            ('/work/hbn28/hbn28e/0121-Mpi270-L32-T96/stout',
             '/arch2/hbn28/hbn28e/0121-Mpi270-L32-T96/stout',),
            ('/work/hbn28/hbn284/eigensystems/0121-Mpi270-L32-T96',),
            (),
        ),
        Ensemble(
            'L = 32 Backward Replica',
            ('/work/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/cfg',
             '/arch2/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/cfg',),
            ('/work/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/stout',
             '/arch2/hbn28/hbn28e/0123-Mpi270-L32-T96-backwards/stout',),
            ('/work/hbn28/hbn284/eigensystems/0123-Mpi270-L32-T96-backwards',),
            (),
        ),
    ]

    for ensemble in ensembles:
        do_ensemble(ensemble)


def do_ensemble(ensemble):
    print(ensemble.name)

    do_type('Gauge (Raw)', ensemble.gauges, regex_cfg)
    do_type('Gauge (Stout)', ensemble.stout, regex_stout)
    do_type('Eigenvalues', ensemble.eigenvalues, regex_eigenvalues)
    do_type('Eigenvectors', ensemble.eigenvalues, regex_eigenvectors)
    do_type('Phases', ensemble.eigenvalues, regex_phases)
    do_perambulator(ensemble.perambulators)
    print()


def do_type(name, directories, regex):
    for directory in directories:
        if not os.path.isdir(directory):
            continue

        files = os.listdir(directory)

        matches = [re.search(regex, filename) for filename in files]
        numbers = sorted([int(list(filter(lambda x: x is not None, m.groups()))[0]) for m in matches if m])
        ranges = list(get_ranges(numbers))
        strides = list(get_strides(ranges))
        #print(name, ', '.join(['{}..{}'.format(*r) for r in ranges]))
        print('  {:15s} {}'.format(name, ', '.join([format_stride(r) for r in strides])))


def do_perambulator(ensemble_paths):
    for ensemble_path in ensemble_paths:
        for flavor in ['light', 'strange']:
            perams = []

            flavor_path = os.path.join(ensemble_path, flavor)
            if not os.path.isdir(flavor_path):
                continue
            for cfg_dir in sorted(os.listdir(flavor_path)):
                rv_avail = []
                m = re.search(r'cnfg(\d+)', cfg_dir)
                if not m:
                    continue
                cfg = int(m.group(1))
                cfg_path = os.path.join(flavor_path, cfg_dir)
                rv_dirs = list(sorted(glob.glob(os.path.join(cfg_path, 'rnd_vec_*'))))
                for rv_dir in rv_dirs:
                    m = re.search(r'rnd_vec_(\d+)', rv_dir)
                    if not m:
                        continue
                    rv = int(m.group(1))
                    rv_path = os.path.join(cfg_path, rv_dir)
                    for filename in sorted(os.listdir(rv_path)):
                        m = re.search(r'perambulator\.rndvec', filename)
                        if m:
                            rv_avail.append(rv)

                if len(rv_avail) == len(rv_dirs):
                    perams.append(cfg)

            ranges = list(get_ranges(perams))
            strides = list(get_strides(ranges))
            formatted = [format_stride(r) for r in strides]

            print('  {:15s} {}'.format('Peram. ' + flavor, ', '.join(formatted)))




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
    if len(ranges) == 1:
        yield ranges[0][0], ranges[0][1], 1
        return

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
