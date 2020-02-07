#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2013, 2017 Martin Ueding <martin-ueding.de>

import functools
import itertools
import math
import operator

import jinja2


def product(values):
    return functools.reduce(operator.mul, values, 1)


def get_geometries(lattice, ranks):
    g_max = [lattice // 16, lattice // 4, lattice // 4, lattice]
    for gx, gy, gz, gt in itertools.product(*[range(m + 1) for m in g_max]):
        if gx * gy * gz * gt == ranks:
            yield (gx, gy, gz, gt)


def main():
    # Setting up Jinja
    env = jinja2.Environment(loader=jinja2.FileSystemLoader('.'))
    template = env.get_template('marconi.sh.j2')

    count = 0

    ranks_per_node = 16
    cores_per_rank = 4
    lattice = 48

    epoch = 6

    for geometry in [
        (2, 4, 2, 1),  #  16,  1
        (2, 4, 2, 2),  #  32,  2
        (2, 4, 2, 4),  #  64,  4
        (2, 4, 2, 8),  # 128,  8
        (2, 4, 4, 8),  # 256, 16
    ]:
        nodes = product(geometry) // ranks_per_node
        for threads in [1, 2, 4]:
            for prec in ['f', 'd']:
                count += 1
                name = 'run{:03d}_nodes{}_cpr{}_s{}_lattice{}_geom{}_prec{}'.format(epoch, nodes, cores_per_rank, threads, lattice, '-'.join(map(str, geometry)), prec)

                rendered = template.render(
                    cores_per_rank=cores_per_rank,
                    geom=geometry,
                    lattice=lattice,
                    nodes=nodes,
                    threads=threads,
                    name=name,
                    ranks_per_node=ranks_per_node,
                    prec=prec,
                )

                with open(name + '.sh', 'w') as f:
                    f.write(rendered)

    print('Jobs:', count)
    print('Jobs * Cores:', count * 68)


if __name__ == "__main__":
    main()
