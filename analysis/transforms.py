#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import collections
import glob
import os

import numpy as np


def convert_to_md_time(dirname, name_in):
    file_in = os.path.join(dirname, 'extract-md_time.tsv')
    data = np.atleast_2d(np.loadtxt(file_in))

    if data.shape[1] == 0:
        return

    update_no = data[:, 0]
    md_time = data[:, 1]

    data = np.atleast_2d(np.loadtxt(os.path.join(dirname, 'extract-{}.tsv'.format(name_in))))
    update_no_2 = data[:, 0]
    y = data[:, 1]

    eq = update_no == update_no_2
    if (isinstance(eq, bool) and not eq) or (isinstance(eq, np.ndarray) and not all(eq)):
        assert False, "Update Numbers must match for {}.\n{}\n{}".format(name_in, str(update_no), str(update_no_2))

    np.savetxt(os.path.join(dirname, 'extract-{}-vs-md_time.tsv'.format(name_in)),
               np.column_stack([md_time, y]))


def convert_time_to_minutes(dirname):
    file_in = os.path.join(dirname, 'extract-seconds_for_trajectory.tsv')
    data = np.atleast_2d(np.loadtxt(file_in))

    if data.shape[1] == 0:
        return

    update_no = data[:, 0]
    seconds = data[:, 1]

    np.savetxt(os.path.join(dirname, 'extract-minutes_for_trajectory.tsv'),
               np.column_stack([update_no, seconds / 60]))


def convert_tau0_to_md_time(dirname):
    file_in = os.path.join(dirname, 'extract-tau0.tsv')
    data = np.loadtxt(file_in)
    update_no = data[:, 0]
    tau0 = data[:, 1]
    md_time = np.cumsum(tau0)

    assert tau0.shape == md_time.shape

    np.savetxt(os.path.join(dirname, 'extract-md_time.tsv'),
               np.column_stack([update_no, md_time]))
