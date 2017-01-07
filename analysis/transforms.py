#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import collections
import glob
import json
import os

import numpy as np

import util


PERCENTILE_LOW = 50 - 34.13
PERCENTILE_HIGH = 50 + 34.13


def get_multiple_percentiles(datas):
    y = np.array([np.percentile(data, 50) for data in datas])
    yerr_down = y - np.array([np.percentile(data, PERCENTILE_LOW) for data in datas])
    yerr_up = np.array([np.percentile(data, PERCENTILE_HIGH) for data in datas]) - y
    return y, yerr_down, yerr_up


def get_percentiles(data):
    y = np.percentile(data, 50)
    yerr_down = y - np.percentile(data, PERCENTILE_LOW)
    yerr_up = np.percentile(data, PERCENTILE_HIGH) - y
    return y, yerr_down, yerr_up


def gflops_per_node_converter(solver_data, update_data):
    gflops_dist = solver_data['gflops']
    nodes = update_data['nodes']
    return get_percentiles(gflops_dist)


def iteration_converter(solver_data, update_data):
    gflops_dist = solver_data['iters']
    return get_percentiles(gflops_dist)


def residual_converter(solver_data, update_data):
    gflops_dist = solver_data['residuals']
    return get_percentiles(gflops_dist)


#subgrid_volume = update_data['subgrid_volume']


def convert_solver_list(dirname, converter, outname):
    filename_in = os.path.join(dirname, 'extract-log.json')

    if not os.path.isfile(filename_in):
        print('File is missing:', filename_in)
        return

    with open(filename_in) as f:
        data = json.load(f)

    results = collections.defaultdict(list)

    for update_no, update_data in sorted(data.items()):
        for solver, solver_data in update_data['solvers'].items():
            try:
                result = list(converter(solver_data, update_data))
            except KeyError as e:
                print(filename_in, e)
                continue

            results[solver].append([float(update_no)] + result)


    for solver, solver_results in results.items():
        if len(solver_results) > 0:
            np.savetxt(os.path.join(
                dirname,
                'extract-solver-{}-{}.tsv'.format(util.make_safe_name(solver), outname)),
                solver_results)


def merge_dict_2(base, add):
    for key1, val1 in add.items():
        for key2, val2 in val1.items():
            base[key1][key2] += val2


def prepare_solver_iters(dirname):
    with open(os.path.join(dirname, 'extract-solver_iters.json')) as f:
        data = json.load(f)

    for solver, tuples in sorted(data.items()):
        x = sorted(map(float, tuples.keys()))
        datas = [gflops for subgrid_volume, gflops in sorted(tuples.items())]
        y, yerr_down, yerr_up = percentiles(datas)

        np.savetxt(os.path.join(dirname, util.make_safe_name('extract-solver_iters-{}.tsv'.format(solver))),
                   np.column_stack([x, y, yerr_down, yerr_up]))


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

    update_no, tau0 = util.load_columns(file_in)
    md_time = np.cumsum(tau0)

    assert tau0.shape == md_time.shape

    np.savetxt(os.path.join(dirname, 'extract-md_time.tsv'),
               np.column_stack([update_no, md_time]))
