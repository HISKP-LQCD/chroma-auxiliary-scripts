#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import subprocess


def get_squeue_output():
    return subprocess.check_output(['squeue']).decode().strip().split('\n')


def get_occupied_nodes(line):
    '''
    >>> get_occupied_nodes('           2729119     devel wilson-c   hbn28e  R       8:41      8 jrc[0036-0043]')
    ('devel', 'R', 8)
    '''
    words = line.split()
    job_id, partition, job, user, state, run_time, nodes, nodelist = words
    return partition, state, int(nodes)


def main():
    options = _parse_args()

    lines = get_squeue_output()
    parsed = map(get_squeue_output, lines)
    running = filter(lambda x: x[1] == 'R', running)

    totals = {}
    for partition, nodes in running:
        if not partition in totals:
            totals[partition] = 0
        totals[partition] += nodes

    print(totals)




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
