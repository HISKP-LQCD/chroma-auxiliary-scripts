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

patterns_resiuals = {
    #'invcg2': re.compile(r'CG_SOLVER: (\d+) iterations.*'),
    #'minvcg': re.compile(r'MInvCG2: (\d+) iterations'),
    'QPhiX Clover M-Shift CG': re.compile(r'shift[0]  Actual \|\| r \|\| / \|\| b \|\| = ([\d.e+-]+)'),
    #'QPhiX Clover BICGSTAB': re.compile(r'QPHIX_CLOVER_BICGSTAB_SOLVER: (\d+) iters,.*'),
    'QPhiX Clover CG': re.compile(r'QPHIX_CLOVER_CG_SOLVER: \|\| r \|\| / \|\| b \|\| = ([\d.e+-]+)'),
}


def main(options):
    pp = pprint.PrettyPrinter()

    for dirname in options.dirname:
        results = {}

        for filename in glob.glob(os.path.join(dirname, '*.out.txt')):
            parse_log_file_to_shards(filename)


        json_file = os.path.join(dirname, 'extract-log.json')
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=4, sort_keys=True)


def get_log_shard_name(logfile):
    dirname = os.path.dirname(logfile)
    basename = os.path.basename(logfile)
    return os.path.join(dirname, 'shard-' + basename + '.json')


def parse_logfile_to_shard(logfile):
    common = {}
    results = {}

    bucket_before = []
    bucket_update = collections.defaultdict(list)

    with open(logfile) as f:
        bucket = bucket_before
        for line in f:
            m = doing_update_pattern.search(line)
            if m:
                update_no = int(m.group(1))
                bucket = bucket_update[update_no]

            bucket.append(line)

    for line in bucket_before:
        for key, (transform, pattern) in patterns_before.items():
            m = pattern.match(line)
            if m:
                common[key] = transform(m.group(1))

    for update_no, lines in sorted(bucket_update.items()):
        results[update_no] = parse_update_block(lines)

        # Copy common fields for each update.
        for key, val in common.items():
            results[update_no][key] = val

    shard_file = get_log_shard_name(logfile)
    with open(shard_file, 'w') as f:
        json.dump(results, f, indent=4, sort_keys=True)


def parse_update_block(lines):
    update_results = {
        'solvers': collections.defaultdict(lambda: collections.defaultdict(list)),
    }

    for line in lines:
        for solver, pattern in patterns_gflops.items():
            m = pattern.match(line)
            if m:
                gflops = float(m.group(1))
                update_results['solvers'][solver]['gflops'].append(gflops)

        for solver, pattern in patterns_iterations.items():
            m = pattern.match(line)
            if m:
                iters = float(m.group(1))
                update_results['solvers'][solver]['iters'].append(iters)

        for solver, pattern in patterns_resiuals.items():
            m = pattern.search(line)
            if m:
                try:
                    iters = float(m.group(1))
                except TypeError:
                    print(m)
                    print(m.groups())
                    raise
                else:
                    update_results['solvers'][solver]['residuals'].append(iters)

    return update_results
    


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
