#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import json
import collections
import os

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op


def main(options):
    options.dirname.sort()

    plot_generic(options.dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 0.0)', 'Plaquette')
    plot_generic(options.dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 0.0)', 'Plaquette')

    plot_generic(options.dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy', transform_delta_h)
    plot_generic(options.dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time)

    plot_generic(options.dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory')

    plot_perf(options.dirname)


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    ax.legend(loc='best', prop={'size': 8})


def dandify_figure(fig):
    fig.tight_layout()


def plot_perf(dirnames):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for dirname in dirnames:
        filename = os.path.join(dirname, 'extract-log.json')

        if not os.path.isfile(filename):
            print('File is missing:', filename)
            continue


        with open(filename) as f:
            data = json.load(f)

        solvers = collections.defaultdict(list)

        for update_no, solver_data in sorted(data['updates'].items()):
            for solver, details in solver_data.items():
                gflops = details['gflops']
                iters = details['iters']
                solvers[solver].append((update_no, np.mean(gflops), np.std(gflops)))

        for solver, tuples in sorted(solvers.items()):
            x, y, yerr = zip(*tuples)
            ax.errorbar(x, y, yerr, marker='o', label=solver)

    ax.set_title('Solver Performance')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'Gflop/s per Node')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-perf.pdf')
    pl.savefig('plot-perf.png')


def transform_delta_h(x, y):
    sel = x > 10
    return x[sel], y[sel]


def transform_delta_h_md_time(x, y):
    sel = x > 0.1
    return x[sel], y[sel]


def plot_generic(dirnames, name, xlabel, ylabel, title, transform=lambda x, y: (x, y)):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for dirname in dirnames:
        filename = os.path.join(dirname, 'extract-{}.tsv'.format(name))
        data = np.loadtxt(filename)
        label = os.path.basename(os.path.realpath(dirname))
        x = data[:, 0]
        y = data[:, 1]
        x, y = transform(x, y)
        ax.plot(x, y, marker='o', label=label)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-{}.pdf'.format(name))
    pl.savefig('plot-{}.png'.format(name))


def make_safe_name(name):
    return ''.join([c for c in name.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_'])
