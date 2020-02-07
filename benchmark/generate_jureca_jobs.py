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
    template = env.get_template('jureca.j2.sh')

    count = 0
    for nodes in [1, 2, 4, 8, 16, 32, 81, 64, 128]:
        for ranks_per_node in [1, 2]:
            cores_per_rank = 24 // ranks_per_node
            for lattice in [32, 48, 64]:
                for geometry in get_geometries(lattice, nodes * ranks_per_node):
                    print(geometry, product(geometry))
                    count += 1
                    name = 'run_nodes{}_rpn{}_lattice{}_geom{}'.format(nodes, ranks_per_node, lattice, '-'.join(map(str, geometry)))

                    rendered = template.render(
                        cores_per_rank=cores_per_rank,
                        geom=geometry,
                        lattice=lattice,
                        nodes=nodes,
                        name=name,
                        ranks_per_node=ranks_per_node,
                    )

                    # Rendering LaTeX document with values.
                    with open(name + '.sh', 'w') as f:
                        f.write(rendered)

    print(count)


if __name__ == "__main__":
    main()
