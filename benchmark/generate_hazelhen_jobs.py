#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2013, 2017 Martin Ueding <mu@martin-ueding.de>

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
    template = env.get_template('hazel-hen.sh.j2')

    epoch = 15
    count = 0
    lattice = 32
    for geometry in get_geometries(lattice, 64):
        nodes = product(geometry)
        print(geometry, nodes)
        count += 1
        name = 'run{:03d}_nodes{}_lattice{}_geom{}'.format(epoch, nodes, lattice, '-'.join(map(str, geometry)))

        rendered = template.render(
            geom=geometry,
            lattice=lattice,
            name=name,
            nodes=nodes,
        )

        with open(name + '.sh', 'w') as f:
            f.write(rendered)

    print(count)


if __name__ == "__main__":
    main()
