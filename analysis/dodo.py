#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import glob
import itertools
import os

import extractors
import transforms
import visualizers

os.chdir('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/Runs')

directories = list(filter(os.path.isdir, os.listdir()))


def task_logfiles_to_shards():
    for directory in directories:
        shard_names = []
        for logfile in glob.glob(os.path.join(directory, 'hmc.slurm-*.out.txt')):
            shard_name = extractors.logfile.get_log_shard_name(logfile)
            shard_names.append(shard_name)

            yield {
                'actions': [(extractors.logfile.parse_logfile_to_shard, [logfile])],
                'basename': 'logfile_to_shards',
                'name': logfile,
                'file_dep': [logfile],
                'targets': [shard_name],
            }

        merged_name = os.path.join(directory, 'extract-log.json')

        yield {
            'actions': [(transforms.merge_json_shards, [shard_names, merged_name])],
            'basename': 'merge_logfile_shards',
            'name': merged_name,
            'file_dep': shard_names,
            'targets': [merged_name],
        }


def task_transform_solver_data():
    for directory in directories:
        for converter, outname in [(transforms.gflops_per_node_converter, 'gflops_per_node'), (transforms.iteration_converter, 'iters'), (transforms.residual_converter, 'residuals')]:
            yield {
                'actions': [(transforms.convert_solver_list, [directory, converter, outname])],
                'name': directory + '/' + outname,
                'file_dep': [os.path.join(directory, 'extract-log.json')],
                'targets': [],
            }


def task_xpath_shards():
    for directory in directories:
        for key, extractor in extractors.xmlfile.bits.items():
            shard_names = []
            for xml_file in itertools.chain(glob.glob(os.path.join(directory, 'hmc.slurm-*.out.xml')),
                                            glob.glob(os.path.join(directory, 'hmc.slurm-*.log.xml'))):
                shard_name = extractors.xmlfile.get_xpath_shard_name(xml_file, key)
                shard_names.append(shard_name)
                yield {
                    'actions': [(extractors.xmlfile.extractor_to_shard, [extractor, xml_file, key])],
                    'name': shard_name,
                    'basename': 'xpath_to_shard',
                    'file_dep': [xml_file],
                    'targets': [shard_name],
                }

            merged_name = os.path.join(directory, 'extract-{}.tsv'.format(key))

            yield {
                'actions': [(transforms.merge_tsv_shards, [shard_names, merged_name])],
                'basename': 'merge_xml_shards',
                'name': merged_name,
                'file_dep': shard_names,
                'targets': [merged_name],
            }


def task_convert_delta_delta_h():
    for dirname in directories:
        in_files = [os.path.join(dirname, 'extract-DeltaDeltaH.tsv'),
                    os.path.join(dirname, 'extract-deltaH.tsv')]
        out_file = os.path.join(dirname, 'extract-DeltaDeltaH_over_DeltaH.tsv')
        yield {
            'actions': [(transforms.delta_delta_h, [dirname])],
            'name': dirname,
            'file_dep': in_files,
            'targets': [out_file],
        }


def task_convert_time_to_minutes():
    for dirname in directories:
        in_files = [os.path.join(dirname, 'extract-seconds_for_trajectory.tsv')]
        out_files = [os.path.join(dirname, 'extract-minutes_for_trajectory.tsv')]
        yield {
            'actions': [(transforms.convert_time_to_minutes, [dirname])],
            'name': dirname,
            'file_dep': in_files,
            'targets': out_files,
        }


def task_convert_t0_to_md_time():
    for dirname in directories:
        in_files = [os.path.join(dirname, 'extract-tau0.tsv')]
        out_files = [os.path.join(dirname, 'extract-md_time.tsv')]
        yield {
            'actions': [(transforms.convert_tau0_to_md_time, [dirname])],
            'name': dirname,
            'file_dep': in_files,
            'targets': out_files,
        }


def plot_generic(dirname, name, *args, **kwargs):
    return {
        'actions': [(visualizers.plot_generic, [[dirname], name] + list(args), kwargs)],
        'name': dirname + '/' + name,
        'file_dep': [os.path.join(dirname, 'extract-{}.tsv'.format(name))],
        'targets': [os.path.join(dirname, 'plot-{}.pdf'.format(name))],
    }


def task_make_plot():
    for dirname in directories:
        yield plot_generic(dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 1.0)', 'Plaquette')
        #yield plot_generic(dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 1.0)', 'Plaquette')

        yield plot_generic(dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy')
        #yield plot_generic(dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time)

        yield plot_generic(dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory')

        yield plot_generic(dirname, 'n_steps', 'Update Number', r'Step Count (coarsest time scale)', 'Integration Steps')
        #yield plot_generic(dirname, 'n_steps-vs-md_time', 'MD Time', r'Step Count (coarsest time scale)', 'Integration Steps')

        yield plot_generic(dirname, 'md_time', 'Update Number', r'MD Time', 'MD Distance')
        yield plot_generic(dirname, 'tau0', 'Update Number', r'MD Step Size', 'MD Step Size')

        yield plot_generic(dirname, 'DeltaDeltaH', 'Update Number', r'$\Delta \Delta H$', 'Reversibility')
        yield plot_generic(dirname, 'DeltaDeltaH_over_DeltaH', 'Update Number', r'$\Delta \Delta H / \Delta H$', 'Reversibility')

        #yield plot_generic(dirname, 't0', 'Update Number', r'$t_0$', 'Wilson Flow Scale Setting')
        #yield plot_generic(dirname, 'w0', 'Update Number', r'$w_0$', 'Wilson Flow Scale Setting')
