#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import json
import collections
import os

import matplotlib.pyplot as pl
import numpy as np


def main(options):
    options.dirname.sort()

    plot_solver_iters(options.dirname)
    plot_perf(options.dirname)
    plot_perf_vs_sublattice(options.dirname)

    plot_generic(options.dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 0.0)', 'Plaquette')
    plot_generic(options.dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 0.0)', 'Plaquette')

    plot_generic(options.dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy', transform_delta_h)
    plot_generic(options.dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time)

    plot_generic(options.dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory')

    plot_generic(options.dirname, 'n_steps', 'Update Number', r'Step Count (coarsest time scale)', 'Integration Steps')
    plot_generic(options.dirname, 'n_steps-vs-md_time', 'MD Time', r'Step Count (coarsest time scale)', 'Integration Steps')

    plot_generic(options.dirname, 'md_time', 'Update Number', r'MD Time', 'MD Distance')
    plot_generic(options.dirname, 'md_time', 'Update Number', r'MD Step Size', 'MD Step Size', transform_step_size, outname='step_size')


def transform_step_size(x, y):
    new_x = x[1:]
    new_y = y[1:] - y[:-1]

    return new_x, new_y


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    ax.legend(loc='best', prop={'size': 8})


def dandify_figure(fig):
    fig.tight_layout()


def plot_solver_iters(dirnames):
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

                to_plot[solver][update_no] += iters

    for solver, tuples in sorted(to_plot.items()):
        x = sorted(tuples.keys())
        datas = [gflops for subgrid_volume, gflops in sorted(tuples.items())]
        y, yerr_down, yerr_up = percentiles(datas)

        ax.errorbar(x, y, (yerr_down, yerr_up), marker='o', linestyle='none', label=solver, errorevery=5)

    ax.set_title('Solver Iterations')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'Iteration Count')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-solver_iters-vs-update_no.pdf')
    pl.savefig('plot-solver_iters-vs-update_no.png')


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
                    np.percentile(gflops, PERCENTILE_LOW) / nodes,
                    np.percentile(gflops, PERCENTILE_HIGH) / nodes,
                ))

        for solver, tuples in sorted(solvers.items()):
            x, y, yerr_low, yerr_high = zip(*sorted(tuples))
            label = '{} -- {}'.format(os.path.basename(os.path.realpath(dirname)), solver)
            line, = ax.plot(x, y, marker='o', label=label)
            ax.fill_between(x, np.array(y) - np.array(yerr_low), np.array(y) + np.array(yerr_high), alpha=0.2, color=line.get_color())

    ax.set_title('Solver Performance')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'Gflop/s per Node')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-perf.pdf')
    pl.savefig('plot-perf.png')

PERCENTILE_LOW = 50 - 34.13
PERCENTILE_HIGH = 50 + 34.13


def percentiles(datas):
    y = np.array([np.percentile(data, 50) for data in datas])
    yerr_down = y - np.array([np.percentile(data, PERCENTILE_LOW) for data in datas])
    yerr_up = np.array([np.percentile(data, PERCENTILE_HIGH) for data in datas]) - y

    return y, yerr_down, yerr_up


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

        ax.errorbar(x, y, (yerr_down, yerr_up), marker='o', linestyle='none', label=solver, errorevery=5)

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


def plot_generic(dirnames, name, xlabel, ylabel, title, transform=lambda x, y: (x, y), outname=None):
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

    if outname is None:
        outname = name

    pl.savefig('plot-{}.pdf'.format(outname))
    pl.savefig('plot-{}.png'.format(outname))


def make_safe_name(name):
    return ''.join([c for c in name.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_'])
