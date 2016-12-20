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

    names_w_plaq = [os.path.join(x, 'extract-w_plaq.tsv') for x in options.dirname]
    plot_generic_1d(names_w_plaq, 'Plaquette', r'$1 - \frac{1}{N_\mathrm{c}} \mathrm{Tr}(W_{1\times1})$')

    names_delta_h = [os.path.join(x, 'extract-deltaH.tsv') for x in options.dirname]
    plot_delta_h(names_delta_h)

    names_seconds = [os.path.join(x, 'extract-seconds_for_trajectory.tsv') for x in options.dirname]
    plot_seconds(names_seconds)

    names_perf = [os.path.join(x, 'extract-perf.json') for x in options.dirname]
    plot_perf(names_perf)


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    ax.legend(loc='best', prop={'size': 8})


def dandify_figure(fig):
    fig.tight_layout()


def plot_perf(filenames):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for filename in filenames:
        with open(filename) as f:
            data = json.load(f)

        solvers = collections.defaultdict(list)

        for update_no, solver_data in sorted(data.items()):
            for solver, gflops in solver_data.items():
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


def plot_delta_h(filenames):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for filename in filenames:
        data = np.loadtxt(filename)
        label = os.path.basename(os.path.dirname(filename))
        update_no = data[:, 0]
        delta_h = data[:, 1]
        sel = update_no > 10
        ax.plot(update_no[sel], delta_h[sel], marker='o', label=label)

    ax.set_title('Energy in Molecular Dynamics')
    ax.set_xlabel('Update Number')
    ax.set_ylabel(r'$\Delta H$')

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-delta_h.pdf')
    pl.savefig('plot-delta_h.png')


def plot_seconds(filenames):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for filename in filenames:
        data = np.loadtxt(filename)
        label = os.path.basename(os.path.dirname(filename))
        update_no = data[:, 0]
        delta_h = data[:, 1]
        ax.plot(update_no, delta_h, marker='o', label=label)

    ax.set_title('Time for Trajectory')
    ax.set_xlabel('Update Number')
    ax.set_ylabel('Seconds')

    twin = ax.twinx()
    twin.set_ylabel('Minutes')
    ymin, ymax = ax.get_ylim()
    twin.set_ylim(ymin / 60, ymax / 60)

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-time_for_trajectory.pdf')
    pl.savefig('plot-time_for_trajectory.png')


def plot_generic_1d(filenames, title, ylabel, xlabel='Update Number'):
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    for filename in filenames:
        data = np.loadtxt(filename)
        label = os.path.basename(os.path.dirname(filename))
        ax.plot(data[:, 0], data[:, 1], marker='o', label=label)

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    dandify_axes(ax)
    dandify_figure(fig)

    pl.savefig('plot-{}.pdf'.format(make_safe_name(title)))
    pl.savefig('plot-{}.png'.format(make_safe_name(title)))


def make_safe_name(name):
    return ''.join([c for c in name.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_'])


