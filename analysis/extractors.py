#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import collections
import os

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op


def main(options):
    print(options)

    groups = group_files(options.xml_file)

    for dirname, files in sorted(groups.items()):
        for key, extractor in bits.items():
            update_no_list, number_list = extractor(files)

            outfile = os.path.join(dirname, 'extract-{}.tsv'.format(key))
            np.savetxt(outfile, np.column_stack([update_no_list, number_list]))


def group_files(filenames):
    groups = collections.defaultdict(list)
    for xml_file in filenames:
        dirname = os.path.dirname(xml_file)
        basename = os.path.basename(xml_file)
        groups[dirname].append(xml_file)
    return groups


def make_xpath_extractor(xpath):
    def extractor(xml_files):
        return extract_xpath_from_all(xml_files, xpath)
    return extractor


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
            print('Update:', update_no)
            update_no_list.append(update_no)

            number_list_local = []

            matches = update.xpath(xpath)
            assert len(matches) == 1
            number = float(matches[0])
            print(xpath, number)
            number_list.append(number)

    return update_no_list, number_list


bits = {
    'w_plaq': make_xpath_extractor('.//w_plaq/text()'),
    'deltaH': make_xpath_extractor('.//deltaH/text()'),
    'seconds_for_trajectory': make_xpath_extractor('.//seconds_for_trajectory/text()'),
}
