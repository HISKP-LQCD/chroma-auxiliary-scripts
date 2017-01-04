#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import glob
import json
import os
import pprint
import re

import numpy as np

import extractors

patterns_before = {
    'nodes': (int, re.compile(r'  total number of nodes = (\d+)')),
    #'jobid' = re.compile(r'\D(\d{6})\D')
    'subgrid_volume': (int, re.compile(r'  subgrid volume = (\d+)')),
}

doing_update_pattern = re.compile(r'Doing Update: (\d+)')

patterns_gflops = {
    'invcg2': re.compile(r'QDP:FlopCount:invcg2 Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'minvcg': re.compile(r'QDP:FlopCount:minvcg Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'QPhiX Clover M-Shift CG': re.compile(r'QPHIX_CLOVER_MULTI_SHIFT_CG_MDAGM_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover BICGSTAB': re.compile(r'QPHIX_CLOVER_BICGSTAB_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover CG': re.compile(r'QPHIX_CLOVER_CG_SOLVER: .* Performance=([\d.]+) GFLOPS'),
}

patterns_iterations = {
    'invcg2': re.compile(r'CG_SOLVER: (\d+) iterations.*'),
    'minvcg': re.compile(r'MInvCG2: (\d+) iterations'),
    'QPhiX Clover M-Shift CG': re.compile(r'QPHIX_CLOVER_MULTI_SHIFT_CG_MDAGM_SOLVER: Iters=(\d+) .*'),
    'QPhiX Clover BICGSTAB': re.compile(r'QPHIX_CLOVER_BICGSTAB_SOLVER: (\d+) iters,.*'),
    'QPhiX Clover CG': re.compile(r'QPHIX_CLOVER_CG_SOLVER: (\d+) iters,.*'),
}


def main(options):
    pp = pprint.PrettyPrinter()

    per_update = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(dict)))

    for dirname in options.dirname:
        for filename in glob.glob(os.path.join(dirname, '*.out')):
            extractors.print_progress(filename)

            bucket_before = []
            bucket_update = collections.defaultdict(list)

            with open(filename) as f:
                bucket = bucket_before
                for line in f:
                    m = doing_update_pattern.search(line)
                    if m:
                        update_no = int(m.group(1))
                        bucket = bucket_update[update_no]

                    bucket.append(line)

            results = {}

            for line in bucket_before:
                for key, (transform, pattern) in patterns_before.items():
                    m = pattern.match(line)
                    if m:
                        results[key] = transform(m.group(1))

            all_gflops = {}
            all_iters = {}

            for update_no, lines in sorted(bucket_update.items()):
                gflops, iters = parse_update_block(lines)
                all_gflops[update_no] = gflops
                all_iters[update_no] = iters

            for update_no, solver_data in all_gflops.items():
                for key, val in results.items():
                    per_update[update_no][key] = val
                for solver, gflops in solver_data.items():
                    per_update[update_no]['solvers'][solver]['gflops'] = gflops

            for update_no, solver_data in all_iters.items():
                for solver, iters in solver_data.items():
                    per_update[update_no]['solvers'][solver]['iters'] = iters

        json_file = os.path.join(dirname, 'extract-log.json')
        with open(json_file, 'w') as f:
            json.dump(per_update, f, indent=4, sort_keys=True)


def parse_update_block(lines):
    results_gflops = collections.defaultdict(list)
    results_iter = collections.defaultdict(list)

    for line in lines:
        for solver, pattern in patterns_gflops.items():
            m = pattern.match(line)
            if m:
                gflops = float(m.group(1))
                results_gflops[solver].append(gflops)

    for line in lines:
        for solver, pattern in patterns_iterations.items():
            m = pattern.match(line)
            if m:
                iters = float(m.group(1))
                results_iter[solver].append(iters)

    return results_gflops, results_iter
    


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('dirname', nargs='+')

    options = parser.parse_args()
    main(options)


if __name__ == '__main__':
    _parse_args()
