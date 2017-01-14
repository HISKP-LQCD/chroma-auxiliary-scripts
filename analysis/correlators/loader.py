# Copyright © 2014-2015, 2017 Martin Ueding <dev@martin-ueding.de>

import util


def folded_list_loader(filenames):
    all_folded = []

    for filename in filenames:
        t, re, im = util.load_columns(filename)

        n = len(t)
        for a in [re, im]:
            second_rev = a[n//2+1:][::-1]
            first = a[:n//2+1]
            first[1:-1] += second_rev
            first[1:-1] /= 2.

        all_folded.append((t, re, im))

    return all_folded
