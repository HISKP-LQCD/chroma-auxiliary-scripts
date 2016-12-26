#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import math
import re


def main():
    options = _parse_args()

    pattern_update = re.compile(r'Doing Update: (\d+) warm_up_p = \d+')
    pattern_total_time = re.compile(r'HMC: total time = ([\d.]+) secs')

    updates = []
    total_time = None

    with open(options.logfile) as f:
        for line in f:
            m = pattern_update.match(line)
            if m:
                updates.append(int(m.group(1)))
                continue
            m = pattern_total_time.match(line)
            if m:
                total_time = float(m.group(1))

    print(updates)
    print(total_time)

    avg = total_time / len(updates)

    max_wtime = 5.3 * 3600

    recommended = math.floor(max_wtime / avg)

    print('Recommended:', recommended)
    print('Time estimated:', recommended * avg / 3600)



def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('logfile')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
