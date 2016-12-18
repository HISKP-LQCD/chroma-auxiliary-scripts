#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import os

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    ax.legend(loc='best')


def dandify_figure(fig):
    fig.tight_layout()


def xpath_to_1d_array(tree, xpath, transform=float):
    return np.array(list(map(transform, tree.xpath(xpath))))


def plot_generic_1d(tree, path_base, xpath, xlabel, ylabel, suffix):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    data = xpath_to_1d_array(tree, xpath)
    ax.plot(data, linestyle='none', marker='o')

    ax.set_title('XPath: {}'.format(xpath))
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig(suffix.format(path_base))


def plot_plaquette(tree, path_base):
    plot_generic_1d(
        tree,
        path_base,
        '//w_plaq/text()',
        'Markov Chain Position',
        'Plaquette',
        '{}-plaquette.pdf',
    )


def plot_deltaH(tree, path_base):
    plot_generic_1d(
        tree,
        path_base,
        '//deltaH/text()',
        'Markov Chain Position',
        r'$\Delta H$',
        '{}-deltaH.pdf',
    )

def plot_seconds_for_trajectory(tree, path_base):
    plot_generic_1d(
        tree,
        path_base,
        '//seconds_for_trajectory/text()',
        'Markov Chain Position',
        r'Seconds for Trajectory',
        '{}-seconds_for_trajectory.pdf',
    )




def main():
    options = _parse_args()

    for xml_file in options.xml_file:
        print('Loading {} …'.format(xml_file))
        path_base, ext = os.path.splitext(xml_file)
        try:
            tree = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            print('XML file could not be loaded')
            print(e)
        else:
            plot_plaquette(tree, path_base)
            plot_deltaH(tree, path_base)
            plot_seconds_for_trajectory(tree, path_base)


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('xml_file', nargs='+')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
