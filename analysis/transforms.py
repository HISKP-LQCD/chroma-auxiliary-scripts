#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

import collections
import glob
import json
import os
import pprint

import numpy as np

import names
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
    gflops_dist = np.array(solver_data['gflops'])
    nodes = update_data['nodes']
    return get_percentiles(gflops_dist / nodes)


def iteration_converter(solver_data, update_data):
    gflops_dist = solver_data['iters']
    return get_percentiles(gflops_dist)


def residual_converter(solver_data, update_data):
    gflops_dist = solver_data['residuals']
    return get_percentiles(gflops_dist)


#subgrid_volume = update_data['subgrid_volume']


def convert_solver_list(dirname, converter, outname):
    filename_in = os.path.join(dirname, 'extract', 'extract-log.json')

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

    to_json = {}

    for solver, solver_results in results.items():
        if len(solver_results) > 0:
            np.savetxt(os.path.join(
                dirname, 'extract',
                'extract-solver-{}-{}.tsv'.format(util.make_safe_name(solver), outname)),
                solver_results)

            to_json[solver] = list(zip(*sorted(solver_results)))

    with open(names.json_extract(dirname, outname), 'w') as f:
        json.dump(to_json, f, indent=4, sort_keys=True)


def merge_json_shards(filenames, dest):
    merged = {}

    for filename in filenames:
        with open(filename) as f:
            data = json.load(f)

        for key, val in data.items():
            assert key not in merged, key
            merged[key] = val

    with open(dest, 'w') as f:
        json.dump(merged, f, indent=4, sort_keys=True)


def merge_dict_2(base, add):
    for key1, val1 in add.items():
        for key2, val2 in val1.items():
            base[key1][key2] += val2


def merge_tsv_shards(shard_names, merged_name):
    all_data = [
        data
        for data in map(np.atleast_2d, map(np.loadtxt, shard_names))
        if data.shape[1] > 0]

    print(all_data)
    if len(all_data) == 0:
        merged = []
    else:
        merged = np.row_stack(all_data)
        merged = util.sort_by_first_column(merged)

    np.savetxt(merged_name, merged)


def prepare_solver_iters(dirname):
    with open(os.path.join(dirname, 'extract', 'extract-solver_iters.json')) as f:
        data = json.load(f)

    for solver, tuples in sorted(data.items()):
        x = sorted(map(float, tuples.keys()))
        datas = [gflops for subgrid_volume, gflops in sorted(tuples.items())]
        y, yerr_down, yerr_up = percentiles(datas)

        np.savetxt(os.path.join(dirname, 'extract', util.make_safe_name('extract-solver_iters-{}.tsv'.format(solver))),
                   np.column_stack([x, y, yerr_down, yerr_up]))


def convert_to_md_time(dirname, name_in):
    file_in = os.path.join(dirname, 'extract', 'extract-md_time.tsv')
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

    np.savetxt(os.path.join(dirname, 'extract', 'extract-{}-vs-md_time.tsv'.format(name_in)),
               np.column_stack([md_time, y]))


def io_delta_h_to_exp(path_in, path_out):
    t, delta_h = util.load_columns(path_in)
    exp = np.exp(- delta_h)
    np.savetxt(path_out, np.column_stack([t, exp]))


def convert_time_to_minutes(dirname):
    file_in = os.path.join(dirname,'extract',  'extract-seconds_for_trajectory.tsv')
    data = np.atleast_2d(np.loadtxt(file_in))

    if data.shape[1] == 0:
        return

    update_no = data[:, 0]
    seconds = data[:, 1]

    np.savetxt(os.path.join(dirname,'extract',  'extract-minutes_for_trajectory.tsv'),
               np.column_stack([update_no, seconds / 60]))


def convert_tau0_to_md_time(file_in, file_out):
    result = []
    try:
        update_no, tau0 = util.load_columns(file_in)
    except ValueError as e:
        print(e)
    else:
        md_time = np.cumsum(tau0)
        assert tau0.shape == md_time.shape
        result = np.column_stack([update_no, md_time])
    np.savetxt(file_out, result)


def delta_delta_h(dirname):
    result = []

    try:
        update_no_ddh, ddh = util.load_columns(os.path.join(dirname,'extract',  'extract-DeltaDeltaH.tsv'))
        update_no_dh, dh = util.load_columns(os.path.join(dirname,'extract',  'extract-deltaH.tsv'))
    except ValueError:
        pass
    else:
        for i, update_no in enumerate(update_no_ddh):
            j = np.where(update_no == update_no_dh)[0][0]
            print(update_no, '->', j)
            result.append((update_no, ddh[i] / dh[j]))

    np.savetxt(os.path.join(dirname,'extract',  'extract-DeltaDeltaH_over_DeltaH.tsv'),
               result)
