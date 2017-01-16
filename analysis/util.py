#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import matplotlib.pyplot as pl
import numpy as np


def load_columns(filename, expected_column_count=None):
    data = np.loadtxt(filename)
    data2d = np.atleast_2d(data)
    shape = data2d.shape
    num_cols = shape[1]

    if num_cols == 0 and expected_column_count is not None:
        cols = [np.array([]) for i in range(expected_column_count)]
    else:
        cols = [data2d[:, i] for i in range(num_cols)]
    return cols


def dandify_axes(ax):
    ax.grid(True)
    ax.margins(0.05)
    ax.legend(loc='best', prop={'size': 8})


def dandify_figure(fig):
    fig.tight_layout()


def make_safe_name(name):
    return ''.join([c for c in name.replace(' ', '_') if ord('A') <= ord(c) <= ord('Z') or ord('a') <= ord(c) <= ord('z') or c in '_.-'])


def make_figure():
    fig = pl.figure()
    ax = fig.add_subplot(1, 1, 1)

    return fig, ax


def save_figure(fig, name):
    ax = fig.add_subplot(1, 1, 1)
    dandify_axes(ax)
    dandify_figure(fig)

    fig.savefig('{}.pdf'.format(name))
    fig.savefig('{}.png'.format(name))


def ignore_missing_files(function):
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except FileNotFoundError as e:
            print('File not found:', e)

    return wrapped


def sort_by_first_column(a):
    return a[a[:, 0].argsort()]
