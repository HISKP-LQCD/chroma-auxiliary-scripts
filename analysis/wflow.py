#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.interpolate
import scipy.optimize

import util

def main(options):
    for xml_file in options.xml:
        convert_xml_to_tsv(xml_file)
        root = find_root(xml_file)
        print(root)
        compute_w(xml_file)
        visualize(xml_file, root=root)


def convert_xml_to_tsv(xml_file):
    tree = etree.parse(xml_file)

    results = tree.xpath('/WilsonFlow/wilson_flow_results')[0]
    wflow_step = results.xpath('wflow_step/text()')[0]
    wflow_gact4i = results.xpath('wflow_gact4i/text()')[0]
    wflow_gactij = results.xpath('wflow_gactij/text()')[0]

    t = np.fromstring(wflow_step, sep=' ')
    temporal = np.fromstring(wflow_gact4i, sep=' ')
    spatial = np.fromstring(wflow_gactij, sep=' ')

    #temporal *= steps**2
    #spatial *= steps**2

    np.savetxt('{}.tsv'.format(xml_file),
               np.column_stack([t, spatial, temporal]))

    np.savetxt('{}.spatial.tsv'.format(xml_file),
               np.column_stack([t, spatial]))
    np.savetxt('{}.temporal.tsv'.format(xml_file),
               np.column_stack([t, temporal]))
    np.savetxt('{}.spatial-t2.tsv'.format(xml_file),
               np.column_stack([t, spatial * t**2]))
    np.savetxt('{}.temporal-t2.tsv'.format(xml_file),
               np.column_stack([t, temporal * t**2]))


def compute_w(xml_file):
    t, spatial, temporal = util.load_columns(xml_file + '.tsv')

    deriv_s = np.gradient(t**2 * spatial, t)
    deriv_t = np.gradient(t**2 * temporal, t)

    w_s = deriv_s * t
    w_t = deriv_t * t

    np.savetxt(xml_file + '.w_s.tsv', np.column_stack([t, w_s]))
    np.savetxt(xml_file + '.w_t.tsv', np.column_stack([t, w_t]))


def find_root(xml_file, threshold=0.3):
    t, spatial, temporal = util.load_columns(xml_file + '.tsv')

    x, y = interpolate_root(t, spatial - threshold)
    return (x, y + threshold)


def interpolate_root(x, y):
    f = scipy.interpolate.interp1d(x, y)
    root = scipy.optimize.brentq(f, np.min(x), np.max(y))
    return root, f(root)


def visualize(xml_file, root=None):
    t, spatial, temporal = util.load_columns(xml_file + '.tsv')

    fig, ax = util.make_figure()

    ax.plot(t, spatial, label='spatial')
    ax.plot(t, temporal, label='temporal')
    ax.plot(t, np.ones(t.shape) * 0.3, label='threshold')

    if root is not None:
        circle = pl.Circle(root, 0.04, fill=False)
        ax.add_artist(circle)

    ax.set_xlabel('Wilson Flow Time')
    ax.set_ylabel('wflow_gact value from Chroma')

    util.save_figure(fig, xml_file + '.tsv')
