#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import collections
import re

import util

patterns = list(map(re.compile, [
    'CG: iter (?P<iter>\d+):  r2 = (?P<r2>[\d.e+-]+)',
    'CG:   iter (?P<iter>\d+): x2 = (?P<x2>[\d.e+-]+)',
]))



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    options = parser.parse_args()

    results = collections.defaultdict(list)

    with open(options.filename) as f:
        for line in f:
            for pattern in patterns:
                m = pattern.search(line)
                if m:
                    gd = m.groupdict()
                    iteration = gd['iter']
                    del gd['iter']
                    key, val = list(gd.items())[0]
                    results[key].append((float(iteration), float(val)))

    fig, ax = util.make_figure()

    for key, data in sorted(results.items()):
        x, y = list(zip(*data))
        ax.loglog(x, y, label=key)
        util.save_columns(options.filename + '-' + key + '.tsv', x, y)

    ax.set_xlabel('Conjugate Gradient Iteration')
    ax.set_ylabel('Spinor Norms')
    ax.set_title(options.filename)


    util.save_figure(fig, options.filename)

            


if __name__ == '__main__':
    main()
