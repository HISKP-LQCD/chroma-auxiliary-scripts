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

measurements = {
    'w_plaq': ('.//w_plaq/text()', 'Plaquette'),
    'deltaH': ('.//deltaH/text()', r'$\Delta H/V$'),
    'seconds_for_trajectory': ('.//seconds_for_trajectory/text()', r'Seconds for Trajectory'),
    'seconds_for_trajectory': ('.//seconds_for_trajectory/text()', r'Seconds for Trajectory'),
}

extracted = collections.defaultdict(dict)

def extract_from_all(xml_files, xpath):
    update_no_list = []
    number_list = []

    for xml_file in xml_files:
        try:
            tree = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            print('XML file could not be loaded')
            print(e)
            continue

        updates = tree.xpath('//Update')

        for update in updates:
            update_no = int(update.xpath('./update_no/text()')[0])
            print('Update:', update_no)
            update_no_list.append(update_no)

            number_list_local = []

            matches = update.xpath(xpath)
            assert len(matches) == 1
            number = float(matches[0])
            print(xpath, number)
            number_list.append(number)

    return update_no_list, number_list


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


def make_safe_name(name):
    return ''.join([c for c in name.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_'])


def main():
    options = _parse_args()

    figs = {key: pl.figure() for key in measurements}
    axs = {key: fig.add_subplot(1, 1, 1) for key, fig in figs.items()}

    groups = collections.defaultdict(list)
    for xml_file in options.xml_file:
        dirname = os.path.dirname(xml_file)
        basename = os.path.basename(xml_file)
        groups[dirname].append(xml_file)

    for group, files in sorted(groups.items()):
        for key, (xpath, ylabel) in measurements.items():
            extracted[key][group] = extract_from_all(files, xpath)

    for run, (update_no, meas) in sorted(extracted['deltaH'].items()):
        y = [x / 16**3 * 32 for x in meas]
        print(np.min(y), np.max(y))
        axs['deltaH'].plot(update_no[1:], y[1:], marker='o', label=os.path.basename(run))

    for run, (update_no, meas) in sorted(extracted['w_plaq'].items()):
        axs['w_plaq'].plot(update_no, meas, marker='o', label=os.path.basename(run))

    for run, (update_no, meas) in sorted(extracted['seconds_for_trajectory'].items()):
        axs['seconds_for_trajectory'].plot(update_no, meas, marker='o', label=os.path.basename(run))

    for key, ax in axs.items():
        ax.set_xlabel('Update Number')
        ax.set_ylabel(measurements[key][1])
        dandify_axes(ax)
    for fig in figs.values():
        dandify_figure(fig)

    for key, fig in figs.items():
        fig.savefig('plot-{}.pdf'.format(make_safe_name(key)))


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
