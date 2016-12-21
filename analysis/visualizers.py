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

    plot_perf(options.dirname)
    plot_perf_vs_sublattice(options.dirname)

    plot_generic(options.dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 0.0)', 'Plaquette')
    plot_generic(options.dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 0.0)', 'Plaquette')

    plot_generic(options.dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy', transform_delta_h)
    plot_generic(options.dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time)

    plot_generic(options.dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory')


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

        for update_no, update_data in sorted(data.items()):
            nodes = update_data['nodes']

            for solver, solver_data in update_data['solvers'].items():
                gflops = solver_data['gflops']
                iters = solver_data['iters']
                solvers[solver].append((int(update_no), np.mean(gflops) / nodes, np.std(gflops) / nodes))

        for solver, tuples in sorted(solvers.items()):
            x, y, yerr = zip(*tuples)
            label = '{} -- {}'.format(os.path.basename(os.path.realpath(dirname)), solver)
            ax.errorbar(x, y, yerr, marker='o', linestyle='none', label=label)

    ax.set_title('Solver Performance')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'Gflop/s per Node')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-perf.pdf')
    pl.savefig('plot-perf.png')


def plot_perf_vs_sublattice(dirnames):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    to_plot = collections.defaultdict(lambda: collections.defaultdict(list))

    for dirname in dirnames:
        filename = os.path.join(dirname, 'extract-log.json')

        if not os.path.isfile(filename):
            print('File is missing:', filename)
            continue

        with open(filename) as f:
            data = json.load(f)

        for update_no, update_data in sorted(data.items()):
            nodes = update_data['nodes']
            subgrid_volume = update_data['subgrid_volume']

            for solver, solver_data in update_data['solvers'].items():
                gflops = solver_data['gflops']
                iters = solver_data['iters']

                to_plot[solver][subgrid_volume] += gflops

    for solver, tuples in sorted(to_plot.items()):
        x = sorted(tuples.keys())
        y = np.array([np.percentile(gflops, 50) / nodes for subgrid_volume, gflops in sorted(tuples.items())])
        yerr_down = y - np.array([np.percentile(gflops, 50 - 34.13) / nodes for subgrid_volume, gflops in sorted(tuples.items())])
        yerr_up = np.array([np.percentile(gflops, 50 + 34.13) / nodes for subgrid_volume, gflops in sorted(tuples.items())]) - y

        ax.errorbar(x, y, (yerr_down, yerr_up), marker='o', linestyle='none', label=solver)

    ax.set_title('Solver Scaling')
    ax.set_xlabel('Subgrid Volume')
    ax.set_ylabel(r'Gflop/s per Node')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-gflops-vs-subgrid_volume.pdf')
    pl.savefig('plot-gflops-vs-subgrid_volume.png')


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
        if not os.path.isfile(filename):
            continue
        data = np.atleast_2d(np.loadtxt(filename))
        if data.shape[1] == 0:
            continue
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
