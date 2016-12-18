#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import collections
import os

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

measurements = [
    ('.//w_plaq/text()', 'Plaquette'),
    ('.//deltaH/text()', r'$\Delta H$'),
    ('.//seconds_for_trajectory/text()', r'Seconds for Trajectory'),
]

scales = [
    None,
    'log',
    None,
]


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


def extract_measurements(xml_file):
    print('Loading {} …'.format(xml_file))
    path_base, ext = os.path.splitext(xml_file)

    try:
        tree = etree.parse(xml_file)
    except etree.XMLSyntaxError as e:
        print('XML file could not be loaded')
        print(e)
        return None, None

    updates = tree.xpath('//Update')

    update_no_list = []
    number_list = []

    for update in updates:
        update_no = int(update.xpath('./update_no/text()')[0])
        print('Update:', update_no)
        update_no_list.append(update_no)

        number_list_local = []

        for xpath, ylabel in measurements:
            matches = update.xpath(xpath)
            assert len(matches) == 1
            number = float(matches[0])
            print(xpath, number)
            number_list_local.append(number)

        number_list.append(number_list_local)

    return update_no_list, zip(*number_list)


def main():
    options = _parse_args()

    figs = [pl.figure() for i in range(len(measurements))]
    axs = [fig.add_subplot(1, 1, 1) for fig in figs]

    groups = collections.defaultdict(list)
    for xml_file in options.xml_file:
        dirname = os.path.dirname(xml_file)
        basename = os.path.basename(xml_file)
        groups[dirname].append(basename)

    for group, files in sorted(groups.items()):
        update_no_group = []
        measured_group_all = [[] for i in measurements]
        for xml_file in files:
            xml_path = os.path.join(group, xml_file)
            update_no, measured_all = extract_measurements(xml_path)

            if update_no is None:
                continue

            update_no_group += update_no
            for measured_group, measured in zip(measured_group_all, measured_all):
                measured_group += measured


        for measured, ax in zip(measured_group_all, axs):
            ax.plot(update_no_group, measured, marker='o', label=os.path.basename(group))

    for ax, fig, yscale, (xpath, ylabel) in zip(axs, figs, scales, measurements):
        ax.set_xlabel('Update Number')
        ax.set_ylabel(ylabel)
        if yscale is not None:
            ax.set_yscale(yscale)
        dandify_axes(ax)
        dandify_figure(fig)
        safe_name = ''.join([c for c in ylabel.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_'])
        fig.savefig('plot-{}.pdf'.format(safe_name))


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
