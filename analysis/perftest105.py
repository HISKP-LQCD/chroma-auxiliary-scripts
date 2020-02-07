#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © YEAR Martin Ueding <martin-ueding.de>

import argparse
import collections
import glob
import itertools
import os
import re

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

import util


def main():
    options = _parse_args()

    pattern = re.compile(r'0105-perf_nodes=(?P<A_nodes>\d+)_ntasks=(?P<B_ntasks>\d+)_cpus=(?P<C_cpus>\d+)_affinity=(?P<E_affinity>\w+?)/')

    pattern_total_time = re.compile('HMC: total time = ([\d.]+) secs')

    rows = []

    for run in options.run:
        print(run)
        m = pattern.match(run)
        if not m:
            continue

        cols1 = m.groupdict()

        nodes = int(cols1['A_nodes'])
        tasks = int(cols1['B_ntasks'])
        cpus = int(cols1['C_cpus'])

        cols1['D_SMT'] = tasks * cpus // 24

        try:
            cols2 = {
                'QPhiX CG Perf': np.loadtxt(os.path.join(run, 'extract-solver-QPhiX_Clover_CG-gflops_per_node.tsv'))[1],
                'QPhiX M-Shift Perf': np.loadtxt(os.path.join(run, 'extract-solver-QPhiX_Clover_M-Shift_CG-gflops_per_node.tsv'))[1],
            }
        except FileNotFoundError as e:
            print(e)
            continue

        logfile = glob.glob(os.path.join(run, 'slurm-*.out'))[0]

        with open(logfile) as f:
            lines = f.readlines()

        m = pattern_total_time.match(lines[-1])
        if m:
            cols2['minutes'] = float(m.group(1)) / 60
        else:
            cols2['minutes'] = 0


        print(cols2.values())

        rows.append((cols1, cols2))

    print()
    print()

    for key in itertools.chain(sorted(cols1.keys()), sorted(cols2.keys())):
        print('{:15s}'.format(str(key)[:13]), end='')
    print()

    for cols1, cols2 in rows:
        for key, value in itertools.chain(sorted(cols1.items()), sorted(cols2.items())):
            print('{:15s}'.format(str(value)[:13]), end='')
        print()


    for x in cols1.keys():
        for y in cols2.keys():
            fig, ax = util.make_figure()
            data = collections.defaultdict(list)
            for c1, c2 in rows:
                data[c1[x]].append(c2[y])
            d = [value for key, value in sorted(data.items())]
            l = [key for key, value in sorted(data.items())]
            ax.boxplot(d, labels=l)
            ax.set_xlabel(x)
            ax.set_ylabel(y)

            util.save_figure(fig, 'boxplot-{}-{}'.format(x, y))




def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('run', nargs='+')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
