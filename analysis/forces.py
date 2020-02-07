#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <martin-ueding.de>

import argparse
import os
import pprint
import subprocess

from lxml import etree
import jinja2
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    #ax.legend(loc='best')


def dandify_figure(fig):
    fig.tight_layout()


def main():
    options = _parse_args()

    pp = pprint.PrettyPrinter()

    print('Loading XML …')
    tree = etree.parse(options.xml_file)

    print('Extracting forces …')
    forces_by_monomial = tree.xpath('//ForcesByMonomial')

    f_avg_dist = {}
    f_max_dist = {}
    f_sq_dist = {}

    for force in forces_by_monomial:
        for elem in force.iterchildren():
            monomial_elem = elem.getchildren()[0]
            monomial = monomial_elem.tag

            if monomial not in f_avg_dist:
                f_avg_dist[monomial] = []
                f_max_dist[monomial] = []
                f_sq_dist[monomial] = []

            f_avg = float(monomial_elem.xpath('Forces/F_avg/text()')[0])
            f_max = float(monomial_elem.xpath('Forces/F_max/text()')[0])
            f_sq = float(monomial_elem.xpath('Forces/F_sq/text()')[0])

            f_avg_dist[monomial].append(f_avg)
            f_max_dist[monomial].append(f_max)
            f_sq_dist[monomial].append(f_sq)


    fig = pl.figure(figsize=(13, 10))
    i = 1
    for dist, title in [(f_avg_dist, 'Average'), (f_max_dist, 'Maximum'), (f_sq_dist, 'Squared')]:
        ll = reversed(sorted(dist.items(), key=lambda x: x[0].lower()))
        keys, values = zip(*ll)
        ax = fig.add_subplot(3, 1, i)
        ax.boxplot(values, labels=keys, vert=False, whis='range')
        xmin, xmax = ax.get_xlim()
        ax.set_xlim(0, xmax)
        ax.set_title(title)
        ax.set_xlabel('Force')
        ax.set_ylabel('Monomial')
        dandify_axes(ax)
        i += 1

    dandify_figure(fig)
    pl.savefig('forces.pdf')
    pl.savefig('forces.png')




def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('xml_file')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
