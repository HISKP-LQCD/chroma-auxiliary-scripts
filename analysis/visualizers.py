#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <mu@martin-ueding.de>

import collections
import glob
import json
import os
import pprint
import re

import matplotlib.pyplot as pl
import numpy as np

import names
import transforms
import util


def plot_solver_data(path_in, path_out, ylabel, title='Solver Data', log_scale=False):
    fig, ax = util.make_figure()

    with open(path_in) as f:
        data = json.load(f)

    for solver, (x, y, yerr_down, yerr_up) in data.items():
        x = np.array(x)
        y = np.array(y)
        yerr_down = np.array(yerr_down)
        yerr_up = np.array(yerr_up)

        label = solver
        p = ax.plot(x, y, label=label)
        ax.fill_between(x, y - yerr_down, y + yerr_up, alpha=0.3, color=p[0].get_color())

    ax.set_title(title)
    ax.set_xlabel('Update Number')
    ax.set_ylabel(ylabel)

    if log_scale:
        ax.set_yscale('log')

    util.dandify_axes(ax)

    if log_scale:
        start, end = ax.get_ylim()
        print(start, end)
        print(end / start)
        if end / start < 15:
            start = 10**int(np.log10(start) - 1)
            end = 10**int(np.log10(end) + 1)
            print('{:.10g} {:.10g}'.format(start, end))
            ax.set_ylim(start, end)

    util.dandify_figure(fig)
    fig.savefig(path_out)


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
                solvers[solver].append((
                    int(update_no),
                    np.median(gflops) / nodes,
                    np.percentile(gflops, transforms.PERCENTILE_LOW) / nodes,
                    np.percentile(gflops, transforms.PERCENTILE_HIGH) / nodes,
                ))

        for solver, tuples in sorted(solvers.items()):
            x, y, yerr_low, yerr_high = zip(*sorted(tuples))
            label = '{} -- {}'.format(os.path.basename(os.path.realpath(dirname)), solver)
            line, = ax.plot(x, y, marker='o', label=label)
            ax.fill_between(x, np.array(y) - np.array(yerr_low), np.array(y) + np.array(yerr_high), alpha=0.2, color=line.get_color())

    ax.set_title('Solver Performance')
    ax.set_xlabel('Update Number (shifted for visibility)')
    ax.set_ylabel(r'Gflop/s per Node')

    util.dandify_axes(ax)
    util.dandify_figure(fig)

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

    util.dandify_axes(ax)
    util.dandify_figure(fig)

    pl.savefig('plot-gflops-vs-subgrid_volume.pdf')
    pl.savefig('plot-gflops-vs-subgrid_volume.png')


def plot_generic(path_in, path_out, xlabel, ylabel, title, use_auto_ylim=False):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    x, y = util.load_columns(path_in, 2)

    if len(x) > 0:
        ax.plot(x, y, marker='o', markersize=2)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)

        if use_auto_ylim:
            ax.set_ylim(get_auto_ylim(y))
        util.dandify_axes(ax)
        util.dandify_figure(fig)

    pl.savefig(path_out)


def get_auto_ylim(y):
    ymin = np.percentile(y, 20)
    ymax = np.percentile(y, 80)
    spread = ymax - ymin
    margin = 2 * spread
    ymin -= margin
    ymax += margin
    return ymin, ymax
