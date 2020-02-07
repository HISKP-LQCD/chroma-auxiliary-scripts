#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <martin-ueding.de>

import argparse
import pprint
import re

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

perf_pattern = re.compile(r'QDP:FlopCount:(\S+) Total performance:  ([\d.]+) Mflops = ([\d.]+) Gflops = ([\d.]+) Tflops')
nodes_pattern = re.compile(r'total number of nodes = (\d+)')
jobid_pattern = re.compile(r'\D(\d{6})\D')
subgrid_volume_pattern = re.compile(r'subgrid volume = (\d+)')

patterns = {
    'invcg2': re.compile(r'QDP:FlopCount:invcg2 Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'minvcg': re.compile(r'QDP:FlopCount:minvcg Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'QPhiX Clover M-Shift CG': re.compile(r'QPHIX_CLOVER_MULTI_SHIFT_CG_MDAGM_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover BICGSTAB': re.compile(r'QPHIX_CLOVER_BICGSTAB_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover CG': re.compile(r'QPHIX_CLOVER_CG_SOLVER: .* Performance=([\d.]+) GFLOPS'),
}


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    #ax.legend(loc='best')


def dandify_figure(fig):
    fig.tight_layout()


def main():
    options = _parse_args()

    pp = pprint.PrettyPrinter()

    perf = {}

    for hmc_log in options.hmc_logs:
        print('Processing {} …'.format(hmc_log))
        nodes = 0
        subgrid_volume = 0
        gflops_dist = []

        m = jobid_pattern.search(hmc_log)
        if m:
            jobid = int(m.group(1))

        with open(hmc_log) as f:
            for line in f:
                m = nodes_pattern.search(line)
                if m:
                    nodes = int(m.group(1))

                m = subgrid_volume_pattern.search(line)
                if m:
                    subgrid_volume = int(m.group(1))

                for solver, pattern in patterns.items():
                    m = pattern.search(line)
                    if m:
                        gflops = float(m.group(1))

                        name = '{} @ {:2d}'.format(solver, nodes)
                        if not name in perf:
                            perf[name] = []
                        perf[name].append(gflops / nodes)

        
    ll = reversed(sorted(perf.items(), key=lambda x: x[0].lower()))
    keys, values = zip(*ll)

    fig = pl.figure(figsize=(10, 6))
    ax = fig.add_subplot(1, 1, 1)
    twin = ax.twiny()
    ax.boxplot(values, labels=keys, vert=False, whis='range')
    xmin, xmax = ax.get_xlim()
    ax.set_xlim(0, xmax)
    twin.set_xlim(0, xmax / (2.5 * 24))
    ax.set_xlabel('GFLOPS per Node')
    twin.set_xlabel('FLOP per Clock per Real Core (24 per Node)')
    ax.set_ylabel('Solver @ Number of Nodes')
    #ax.set_title('USQCD Chroma/hmc Solver Performance on JURECA')
    dandify_axes(ax)
    dandify_figure(fig)
    pl.savefig('performance-flop_per_clock.pdf')
    pl.savefig('performance-flop_per_clock.png')


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('hmc_logs', nargs='+')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
