#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import collections
import glob
import json
import os
import re
import subprocess

import matplotlib.pyplot as pl
import numpy as np

import transforms
import util


def main(options):
    for dirname in options.dirname:
        transforms.convert_solver_list(dirname,
                                       transforms.gflops_per_node_converter, 
                                       'gflops_per_node')
        transforms.convert_solver_list(dirname,
                                       transforms.iteration_converter, 
                                       'iters')

    plot_solver_iters(options.dirname)
    #plot_perf(options.dirname)
    #plot_perf_vs_sublattice(options.dirname)

    plot_generic(options.dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 1.0)', 'Plaquette', shift=options.shift, shift_amount=options.shift_amount)
    plot_generic(options.dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 1.0)', 'Plaquette', shift=options.shift, shift_amount=options.shift_amount)

    plot_generic(options.dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy', transform_delta_h, shift=options.shift, shift_amount=options.shift_amount)
    plot_generic(options.dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time, shift=options.shift, shift_amount=options.shift_amount)

    plot_generic(options.dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy (Zoom)', ax_transform=set_y_limits_delta_h, outname='deltaH-narrow', shift=options.shift, shift_amount=options.shift_amount)

    plot_generic(options.dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory', shift=options.shift, shift_amount=options.shift_amount)

    plot_generic(options.dirname, 'n_steps', 'Update Number', r'Step Count (coarsest time scale)', 'Integration Steps', shift=options.shift, shift_amount=options.shift_amount)
    plot_generic(options.dirname, 'n_steps-vs-md_time', 'MD Time', r'Step Count (coarsest time scale)', 'Integration Steps', shift=options.shift, shift_amount=options.shift_amount)

    plot_generic(options.dirname, 'md_time', 'Update Number', r'MD Time', 'MD Distance', shift=options.shift, shift_amount=options.shift_amount)
    plot_generic(options.dirname, 'tau0', 'Update Number', r'MD Step Size', 'MD Step Size', shift=options.shift, shift_amount=options.shift_amount)

    subprocess.check_call(['pdfunite'] + sorted(glob.glob('plot-*.pdf')) + [options.united_name])


def set_y_limits_delta_h(ax):
    ax.set_ylim(-1, 1)


def plot_solver_iters(dirnames):
    fig, ax = util.make_figure()

    for dirname in dirnames:
        files = glob.glob(os.path.join(dirname, 'extract-solver_iters-*.tsv'))

        for f in files:
            x, y, yerr_down, yerr_up = util.load_columns(f)
            m = re.search(r'extract-solver_iters-(.+?).tsv', f)
            solver_name = m.group(1).replace('_', ' ')
            label = '{}/{}'.format(os.path.basename(os.path.realpath(dirname)), solver_name)
            ax.errorbar(x, y, (yerr_down, yerr_up), marker='o', linestyle='none', label=label)

    ax.set_title('Solver Iterations')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'Iteration Count')

    util.save_figure(fig, 'plot-solver_iters-vs-update_no')


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


def transform_delta_h(x, y):
    sel = x > 10
    return x[sel], y[sel]


def transform_delta_h_md_time(x, y):
    sel = x > 0.1
    return x[sel], y[sel]


def plot_generic(dirnames, name, xlabel, ylabel, title, transform=lambda x, y: (x, y), outname=None, ax_transform=None, shift=False, shift_amount=0.1):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    if shift:
        xlabel += ' (shifted by {} per curve)'.format(shift_amount)

    for i, dirname in enumerate(dirnames):
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
        if shift:
            x = np.array(x) + shift_amount * i
        ax.plot(x, y, marker='o', label=label, markersize=2)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if ax_transform is not None:
        ax_transform(ax)

    util.dandify_axes(ax)
    util.dandify_figure(fig)

    if outname is None:
        outname = name

    pl.savefig('plot-{}.pdf'.format(outname))
    pl.savefig('plot-{}.png'.format(outname))
