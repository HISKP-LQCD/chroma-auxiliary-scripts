#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

import argparse
import collections
import csv
import functools
import itertools
import operator
import os
import pprint
import re

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

def product(values):
    return functools.reduce(operator.mul, values, 1)



general_regexes = [
    r'TIMING IN (?P<precision>\w+) PRECISION',
    r'FT\s+(?P<precision>double|half|float)',

    r'VECLEN ?= ?(?P<veclen>\d+),? SOALEN ?= ?(?P<soalen>\d+)',
    r'veclen\s+(?P<veclen>\d+)',
    r'soalen\s+(?P<soalen>\d+)',

    r'Global Lattice Size =  (?P<Lx>\d+) (?P<Ly>\d+) (?P<Lz>\d+) (?P<Lt>\d+)',
    r'Local Lattice Size =  (?P<lx>\d+) (?P<ly>\d+) (?P<lz>\d+) (?P<lt>\d+)',

    r'Block Sizes: By ?= ?(?P<By>\d+) Bz ?= ?(?P<Bz>\d+)',
    r'Blocking\s+(?P<By>\d+) (?P<Bz>\d+)',

    r'Cores = (?P<Cores>\d+)',
    r'Cores\s+(?P<Cores>\d+)',

    r'SMT Grid: Sy ?= ?(?P<Sy>\d+) Sz ?= ?(?P<Sz>\d+)',
    r'Sy Sz\s+(?P<Sy>\d+) (?P<Sz>\d+)',

    r'Pad Factors: PadXY ?= ?(?P<PadXY>\d+) PadXYZ ?= ?(?P<PadXYZ>\d+)',
    r'PadXY PadXYZ\s+(?P<PadXY>\d+) (?P<PadXYZ>\d+)',

    r'Threads_per_core = (?P<threads_per_core>\d+)',
    r'Declared QMP Topology: (?P<geom1>\d+) (?P<geom2>\d+) (?P<geom3>\d+) (?P<geom4>\d+)',
]

meas_regexes = [
    r'(?P<usec_iter>[\d+-e]+) usec/iteration',
    r'Performance: (?P<gflops_total>[\d+-e]+) GFLOPS total',
    r'(?P<gflops_node>[\d+-e]+) GFLOPS / node',
    r'CG GFLOPS=(?P<cg_gflops>[\d+-e]+)',
]

filename_regexes = [
    r'(?P<affinity>scatter|balanced|compact)'
]


def dandify_axes(ax, legend=False):
    ax.grid(True)
    ax.margins(0.05)
    if legend:
        ax.legend(loc='best')


def dandify_figure(fig):
    fig.tight_layout()


def main():
    options = _parse_args()

    store = {'Dslash': [], 'M': []}

    metas = []

    for filename in options.file:
        with open(filename) as f:
            lines = list(f)

        mode = 'meta'
        meta = {
            'geom1': 1,
            'geom2': 1,
            'geom3': 1,
            'geom4': 1,
        }
        results = collections.defaultdict(lambda: collections.defaultdict(list))

        for regex in filename_regexes:
            m = re.search(regex, os.path.basename(filename))
            if m:
                meta.update(m.groupdict())


        for line in lines:
            if line.startswith('Timing on cb'):
                mode = 'Dslash'
                continue

            if line.startswith('Timing M'):
                mode = 'M'
                continue

            if line.startswith('Initializing CG Solver'):
                mode = 'CG'
                continue

            if mode == 'meta':
                for regex in general_regexes:
                    m = re.search(regex, line)
                    if m:
                        meta.update(m.groupdict())
            else:
                for regex in meas_regexes:
                    m = re.search(regex, line)
                    if m:
                        key, val = list(m.groupdict().items())[0]
                        results[mode][key].append(val)


        if len(results) > 0:
            print(filename)
            for operation, op_data in sorted(results.items()):
                #print(operation)
                for key, vals in sorted(op_data.items()):
                    vals = list(map(float, vals))[1:]
                    #print(key, vals)
                    mean = np.mean(vals)
                    err =  np.std(vals) / np.sqrt(len(vals))

                    if key == 'gflops_total':
                        store[operation].append([
                            int(meta['By']),
                            int(meta['soalen']),
                            meta['precision'],
                            mean,
                            err,
                        ])

                        meta['gflops_total_val'] = mean
                        meta['gflops_total_err'] = err

                    if key == 'cg_gflops':
                        meta['cg_gflops_val'] = mean
                        meta['cg_gflops_err'] = err


            meta['ranks'] = product([int(meta['geom' + str(i)])
                                     for i in range(1, 5)])
            print(meta['Cores'])
            meta['ranks_per_node'] = options.cores_per_node // int(meta['Cores'])
            meta['nodes'] = meta['ranks'] / meta['ranks_per_node']


            #pprint.pprint(meta)
            #print()
            metas.append(meta)

    #pprint.pprint(store)

    ###

    to_plot = collections.defaultdict(list)
    for by, soalen, prec, mean, err in store['Dslash']:
        if by == 8:
            to_plot[prec].append((soalen, mean, err))

    #pprint.pprint(to_plot)

    for prec, prec_data in sorted(to_plot.items()):
        print(r'\addplot[error bars/.cd, y dir=both, y explicit] coordinates {', end='')
        for soalen, mean, err in prec_data:
            print('(', np.log2(soalen), ',', mean, ') +- (0,', err, ') ', end='')
        print(r'};',)
        print(r'\addlegendentry{', prec, '}')


    with open(options.output, 'w') as f:
        writer = csv.DictWriter(f, sorted(metas[0].keys()))
        writer.writeheader()
        for meta in metas:
            writer.writerow(meta)




def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('file', nargs='+')
    parser.add_argument('--output', default='perf.csv')
    parser.add_argument('--cores-per-node', type=int, default=24)
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
