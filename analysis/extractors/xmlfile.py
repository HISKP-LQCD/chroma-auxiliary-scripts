#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import collections
import glob
import os

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

import extractors


def main(options):
    for dirname in options.dirname:
        extractors.print_progress(dirname)
        for key, extractor in bits.items():
            extracted = extractor(dirname)
            if extracted is not None:
                update_no_list, number_list = extracted
                outfile = os.path.join(dirname, 'extract-{}.tsv'.format(key))
                np.savetxt(outfile, np.column_stack([update_no_list, number_list]))

        convert_to_md_time(dirname, 'w_plaq')
        convert_to_md_time(dirname, 'deltaH')
        convert_time_to_minutes(dirname)


def make_xpath_extractor(xpath):
    def extractor(dirname):
        xml_files = glob.glob(os.path.join(dirname, '*.xml'))
        return extract_xpath_from_all(xml_files, xpath)
    return extractor


def extract_md_time(dirname):
    xml_files = glob.glob(os.path.join(dirname, '*.xml'))

    update_no_list = []
    md_time_list = []

    step_sizes = {}

    for xml_file in xml_files:
        try:
            tree = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            print('XML file could not be loaded')
            print(e)
            continue

        if len(tree.xpath('//doHMC')) == 0:
            # This is not an output XML file.
            continue

        tau0 = float(tree.xpath('//hmc/Input/Params/HMCTrj/MDIntegrator/tau0/text()')[0])

        updates = tree.xpath('//Update')

        for update in updates:
            update_no = int(update.xpath('./update_no/text()')[0])

            step_sizes[update_no] = tau0

    md_time = 0.0

    for update_no, tau0 in sorted(step_sizes.items()):
        update_no_list.append(update_no)
        md_time += tau0
        md_time_list.append(md_time)

    return update_no_list, md_time_list


def extract_xpath_from_all(xml_files, xpath):
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

            number_list_local = []

            matches = update.xpath(xpath)
            if len(matches) == 0:
                print("No measurements of {} in XML file {}".format(xpath, xml_file))
                continue

            number = float(matches[0])

            update_no_list.append(update_no)
            number_list.append(number)

    if len(update_no_list) == 0:
        return None

    update_no_list, number_list = zip(*sorted(zip(update_no_list, number_list)))

    return update_no_list, number_list


bits = {
    'w_plaq': make_xpath_extractor('.//w_plaq/text()'),
    'deltaH': make_xpath_extractor('.//deltaH/text()'),
    'seconds_for_trajectory': make_xpath_extractor('.//seconds_for_trajectory/text()'),
    'md_time': extract_md_time,
}


def convert_to_md_time(dirname, name_in):
    file_in = os.path.join(dirname, 'extract-md_time.tsv')
    data = np.atleast_2d(np.loadtxt(file_in))

    if data.shape[1] == 0:
        return

    update_no = data[:, 0]
    md_time = data[:, 1]

    data = np.atleast_2d(np.loadtxt(os.path.join(dirname, 'extract-{}.tsv'.format(name_in))))
    update_no_2 = data[:, 0]
    y = data[:, 1]

    assert all(update_no == update_no_2), "Update Numbers must match.\n{}\n{}".format(str(update_no), str(update_no_2))

    np.savetxt(os.path.join(dirname, 'extract-{}-vs-md_time.tsv'.format(name_in)),
               np.column_stack([md_time, y]))


def convert_time_to_minutes(dirname):
    file_in = os.path.join(dirname, 'extract-seconds_for_trajectory.tsv')
    data = np.atleast_2d(np.loadtxt(file_in))

    if data.shape[1] == 0:
        return

    update_no = data[:, 0]
    seconds = data[:, 1]

    np.savetxt(os.path.join(dirname, 'extract-minutes_for_trajectory.tsv'),
               np.column_stack([update_no, seconds / 60]))
