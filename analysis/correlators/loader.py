# Copyright © 2014-2015, 2017 Martin Ueding <dev@martin-ueding.de>

import util


def folded_list_loader(filenames):
    all_folded = []

    for filename in filenames:
        t, re, im = util.load_columns(filename)

        n = len(t)

        a = re

        second_rev = a[n//2+1:][::-1]
        first = a[:n//2+1]
        first[1:-1] += second_rev
        first[1:-1] /= 2.
        a = first

        all_folded.append(a)

    return all_folded
