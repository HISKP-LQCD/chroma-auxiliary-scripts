#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import glob
import os
import re

from lxml import etree
import matplotlib.pyplot as pl
import numpy as np
import scipy.interpolate
import scipy.optimize

import util


def io_compute_intersection(path_in, path_out):
    root = find_root(path_in)
    result = np.sqrt(root)
    np.savetxt(path_out, [result])


def io_convert_xml_to_tsv(path_in, path_out):
    tree = etree.parse(path_in)

    print(path_in)
    results = tree.xpath('/WilsonFlow/wilson_flow_results')[0]
    wflow_step = results.xpath('wflow_step/text()')[0]
    wflow_gactij = results.xpath('wflow_gactij/text()')[0]

    t = np.fromstring(wflow_step, sep=' ')
    e = np.fromstring(wflow_gactij, sep=' ')
    np.savetxt(path_out, np.column_stack([t, e]))


def io_compute_t2_e(path_in, path_out):
    t, e = util.load_columns(path_in)
    np.savetxt(path_out, np.column_stack([t, t**2 * e]))


def derive_w(t, e, method='gradient'):
    eps = t[1] - t[0]

    if method == 'gradient':
        w = t * np.gradient(t**2 * e, eps)
    elif method == 'chain-gradient':
        grad = np.gradient(e, eps)
        w = t * (2*t * e + t**2 * grad)
    elif method == 'explicit-asym':
        grad = (e[1:] - e[:-1]) / eps
        grad = np.concatenate([grad, [0]])
        w = t * (2*t * e + t**2 * grad)
    elif method == 'explicit-sym':
        grad = (e[2:] - e[:-2]) / (2 * eps)
        grad = np.concatenate([[0], grad, [0]])
        w = t * (2*t * e + t**2 * grad)
    else:
        raise RuntimeError("Method {} is not supported.".format(method))

    return w


def io_compute_w(path_in, path_out):
    t, e = util.load_columns(path_in)
    w = derive_w(t, e)
    np.savetxt(path_out, np.column_stack([t, w]))


def find_root(tsv_file, threshold=0.3):
    t, t2e = util.load_columns(tsv_file)
    x = interpolate_root(t, t2e - threshold)
    return x


def interpolate_root(x, y):
    f = scipy.interpolate.interp1d(x, y)
    upper = x[y > 0]
    if len(upper) == 0:
        return np.nan
    root = scipy.optimize.brentq(f, np.min(x[1:]), np.min(upper))
    return root


def visualize(xml_file, root=None):
    t, t2e = util.load_columns(xml_file + '.t2e.tsv')

    fig = pl.figure(figsize=(16, 9))
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 4)

    ax1.plot(t, t2e)
    ax1.plot(t, np.ones(t.shape) * 0.3)

    if root is not None:
        x, y = root

        #ax2 = pl.axes([.65, .6, .3, .3], axisbg='0.9')
        ax2.plot(t, t2e, marker='o')
        ax2.plot(t, np.ones(t.shape) * 0.3)

        sel = t < 3 * x
        ax3.plot(t[sel], t2e[sel])
        ax3.plot(t[sel], np.ones(t[sel].shape) * 0.3)

        ax1.plot([x], [y], marker='o', alpha=0.3, color='red', markersize=20)
        ax2.plot([x], [y], marker='o', alpha=0.3, color='red', markersize=20)
        ax3.plot([x], [y], marker='o', alpha=0.3, color='red', markersize=20)

        ax2.set_xlim(0.7 * x, 1.3 * x)
        ax2.set_ylim(0.22, 0.38)

    #ax2.locator_params(nbins=6)
    #ax3.locator_params(nbins=6)

    ax1.set_title('All Computed Data')
    ax2.set_title('Interpolation')
    ax3.set_title('First $3 t_0$')

    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel('Wilson Flow Time $t$')
        ax.set_ylabel(r'$t^2 \langle E \rangle$')

        util.dandify_axes(ax)

    util.dandify_figure(fig)

    fig.savefig(xml_file + '.t2e.pdf')


def merge_intersections(paths_in, path_out):
    data = []
    for path_in in paths_in:
        intersection = np.loadtxt(path_in)
        print(intersection)
        if np.isnan(intersection):
            continue
        m = re.search(r'config-(\d+)', path_in)
        update_no = float(m.group(1))

        data.append((update_no, intersection))

    a = np.atleast_2d(np.array(data))
    if a.shape[1] > 0:
        a = util.sort_by_first_column(a)

    np.savetxt(path_out, a)
