#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

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

                m = perf_pattern.search(line)
                if m:
                    task = m.group(1)
                    if task == 'invcg2':
                        gflops = float(m.group(3))
                        gflops_dist.append(gflops)

        if len(gflops_dist) > 0:
            gflops_val = np.mean(gflops_dist)
            gflops_err = np.std(gflops_dist)

            print(nodes, subgrid_volume, gflops_val)


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
