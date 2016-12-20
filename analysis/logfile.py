#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import json
import os
import pprint
import re

import numpy as np

perf_pattern = re.compile(r'QDP:FlopCount:(\S+) Total performance:  ([\d.]+) Mflops = ([\d.]+) Gflops = ([\d.]+) Tflops')
nodes_pattern = re.compile(r'total number of nodes = (\d+)')
jobid_pattern = re.compile(r'\D(\d{6})\D')
subgrid_volume_pattern = re.compile(r'subgrid volume = (\d+)')

doing_update_pattern = re.compile(r'Doing Update: (\d+)')

patterns = {
    'invcg2': re.compile(r'QDP:FlopCount:invcg2 Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'minvcg': re.compile(r'QDP:FlopCount:minvcg Total performance:  [\d.]+ Mflops = ([\d.]+) Gflops = [\d.]+ Tflops'),
    'QPhiX Clover M-Shift CG': re.compile(r'QPHIX_CLOVER_MULTI_SHIFT_CG_MDAGM_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover BICGSTAB': re.compile(r'QPHIX_CLOVER_BICGSTAB_SOLVER: .* Performance=([\d.]+) GFLOPS'),
    'QPhiX Clover CG': re.compile(r'QPHIX_CLOVER_CG_SOLVER: .* Performance=([\d.]+) GFLOPS'),
}


def main(options):
    pp = pprint.PrettyPrinter()

    bucket_before = []
    bucket_update = collections.defaultdict(list)

    with open(options.logfile) as f:
        bucket = bucket_before
        for line in f:
            m = doing_update_pattern.search(line)
            if m:
                update_no = int(m.group(1))
                bucket = bucket_update[update_no]

            bucket.append(line)

    all_gflops = {}

    for update_no, lines in sorted(bucket_update.items()):
        gflops = parse_update_block(lines)
        all_gflops[update_no] = gflops

    #pp.pprint(all_gflops)

    for update_no, solver_data in sorted(all_gflops.items()):
        print(update_no)
        for solver, gflops in sorted(solver_data.items()):
            print(solver, np.mean(gflops), np.std(gflops))
        print()
        
    json_file = os.path.join(os.path.dirname(options.logfile), 'extract-perf.json')
    with open(json_file, 'w') as f:
        json.dump(all_gflops, f, indent=4)


def parse_update_block(lines):
    results = collections.defaultdict(list)
    for line in lines:
        for solver, pattern in patterns.items():
            m = pattern.match(line)
            if m:
                gflops = float(m.group(1))
                results[solver].append(gflops)

    return results
    


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('logfile')

    options = parser.parse_args()
    main(options)


if __name__ == '__main__':
    _parse_args()
