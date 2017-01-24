#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import glob
import itertools
import os
import re

import correlators
import correlators.analysis
import extractors
import names
import transforms
import visualizers
import wflow

os.chdir('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/Runs')

directories = list(filter(os.path.isdir, os.listdir()))


def task_logfiles_to_shards():
    for directory in directories:
        shard_names = []
        for logfile in glob.glob(os.path.join(directory, 'hmc-out', 'hmc.slurm-*.out.txt')):
            shard_name = names.log_shard(logfile)
            shard_names.append(shard_name)

            yield {
                'actions': [(extractors.logfile.parse_logfile_to_shard, [logfile])],
                'basename': 'logfile_to_shards',
                'name': logfile,
                'file_dep': [logfile],
                'targets': [shard_name],
            }

        merged_name = names.log_extract(directory)

        yield {
            'actions': [(transforms.merge_json_shards, [shard_names, merged_name])],
            'basename': 'merge_logfile_shards',
            'name': merged_name,
            'file_dep': shard_names,
            'targets': [merged_name],
        }


def task_transform_solver_data():
    for directory in directories:
        for converter, outname, ylabel, log_scale in [
            (transforms.gflops_per_node_converter, 'gflops_per_node', 'Gflop/s per Node', False),
            (transforms.iteration_converter, 'iters', 'Iterations', False),
            (transforms.residual_converter, 'residuals', 'Residuals', True),
        ]:
            yield {
                'actions': [(transforms.convert_solver_list, [directory, converter, outname])],
                'name': directory + '/' + outname,
                'file_dep': [names.log_extract(directory)],
                'targets': [names.json_extract(directory, outname)],
            }

            path_in = names.json_extract(directory, outname)
            path_out = names.plot(directory, 'solver_' + outname)

            yield {
                'actions': [(visualizers.plot_solver_data, [path_in, path_out, converter, ylabel, log_scale])],
                'name': path_out,
                'file_dep': [path_in],
                'targets': [path_out],
            }


def task_xpath_shards():
    for directory in directories:
        for key, extractor in extractors.xmlfile.bits.items():
            shard_names = []
            for xml_file in itertools.chain(glob.glob(os.path.join(directory, 'hmc-out', 'hmc.slurm-*.out.xml')),
                                            glob.glob(os.path.join(directory, 'hmc-out', 'hmc.slurm-*.log.xml'))):
                shard_name = names.xpath_shard(xml_file, key)
                shard_names.append(shard_name)
                yield {
                    'actions': [(extractors.xmlfile.extractor_to_shard, [extractor, xml_file, key])],
                    'name': shard_name,
                    'basename': 'xpath_to_shard',
                    'file_dep': [xml_file],
                    'targets': [shard_name],
                }

            merged_name = names.xmllog_extract(directory, key)

            yield {
                'actions': [(transforms.merge_tsv_shards, [shard_names, merged_name])],
                'basename': 'merge_xml_shards',
                'name': merged_name,
                'file_dep': shard_names,
                'targets': [merged_name],
            }


def task_convert_delta_delta_h():
    for dirname in directories:
        in_files = [os.path.join(dirname, 'extract', 'extract-DeltaDeltaH.tsv'),
                    os.path.join(dirname,'extract',  'extract-deltaH.tsv')]
        out_file = os.path.join(dirname,'extract',  'extract-DeltaDeltaH_over_DeltaH.tsv')
        yield {
            'actions': [(transforms.delta_delta_h, [dirname])],
            'name': dirname,
            'file_dep': in_files,
            'targets': [out_file],
        }


def task_delta_h_to_exp():
    for dirname in directories:
        yield make_single_transform(dirname,
                                    transforms.io_delta_h_to_exp,
                                    os.path.join(dirname, 'extract', 'extract-deltaH.tsv'),
                                    os.path.join(dirname, 'extract', 'extract-exp_deltaH.tsv'))


def task_convert_time_to_minutes():
    for dirname in directories:
        path_in = os.path.join(dirname, 'extract', 'extract-seconds_for_trajectory.tsv')
        path_out = os.path.join(dirname, 'extract', 'extract-minutes_for_trajectory.tsv')
        yield make_single_transform(dirname,
                                    transforms.io_time_to_minutes,
                                    path_in,
                                    path_out)


def task_convert_t0_to_md_time():
    for dirname in directories:
        yield make_single_transform(dirname,
                                    transforms.convert_tau0_to_md_time,
                                    os.path.join(dirname, 'extract', 'extract-tau0.tsv'),
                                    os.path.join(dirname, 'extract', 'extract-md_time.tsv'))

def task_wflow():
    for dirname in directories:
        files_t0 = []
        files_w0 = []

        for xml_file in glob.glob(os.path.join(dirname, 'wflow', 'wflow.config-*.out.xml')):
            file_e = names.wflow_xml_shard_name(xml_file, 'e')
            file_t2e = names.wflow_xml_shard_name(xml_file, 't2e')
            file_w = names.wflow_xml_shard_name(xml_file, 'w')
            file_t0 = names.wflow_xml_shard_name(xml_file, 't0')
            file_w0 = names.wflow_xml_shard_name(xml_file, 'w0')

            files_t0.append(file_t0)
            files_w0.append(file_w0)

            yield make_single_transform(dirname,
                                        wflow.io_convert_xml_to_tsv,
                                        xml_file,
                                        file_e)
            yield make_single_transform(dirname,
                                        wflow.io_compute_t2_e,
                                        file_e,
                                        file_t2e)
            yield make_single_transform(dirname,
                                        wflow.io_compute_w,
                                        file_e,
                                        file_w)
            yield make_single_transform(dirname,
                                        wflow.io_compute_intersection,
                                        file_t2e,
                                        file_t0)
            yield make_single_transform(dirname,
                                        wflow.io_compute_intersection,
                                        file_w,
                                        file_w0)

        for name, files in [('t0', files_t0), ('w0', files_w0)]:
            path_out = names.wflow_tsv(dirname, name)
            yield {
                'actions': [(wflow.merge_intersections, [files, path_out])],
                'name': path_out,
                'file_dep': files,
                'targets': [path_out],
            }



def make_single_transform(dirname, function, path_in, path_out):
    return {
        'actions': [(function, [path_in, path_out])],
        'name': path_out,
        'file_dep': [path_in],
        'targets': [path_out],
    }


def plot_generic(dirname, name, *args, **kwargs):
    path_in = names.tsv_extract(dirname, name)
    path_out = names.plot(dirname, name)

    yield {
        'actions': [(visualizers.plot_generic, [path_in, path_out] + list(args), kwargs)],
        'name': path_out,
        'file_dep': [path_in],
        'targets': [path_out],
    }

    path_out = names.plot(dirname, name + '_autoy')
    kwargs = dict(kwargs)
    kwargs['use_auto_ylim'] = True

    yield {
        'actions': [(visualizers.plot_generic, [path_in, path_out] + list(args), kwargs)],
        'name': path_out,
        'file_dep': [path_in],
        'targets': [path_out],
    }


def task_make_plot():
    tasks = []
    for dirname in directories:
        tasks.append(plot_generic(dirname, 'w_plaq', 'Update Number', 'Plaquette (cold is 1.0)', 'Plaquette'))
        #tasks.append(plot_generic(dirname, 'w_plaq-vs-md_time', 'MD Time', 'Plaquette (cold is 1.0)', 'Plaquette'))

        tasks.append(plot_generic(dirname, 'deltaH', 'Update Number', r'$\Delta H$', 'MD Energy'))
        #tasks.append(plot_generic(dirname, 'deltaH-vs-md_time', 'MD Time', r'$\Delta H$', 'MD Energy', transform_delta_h_md_time))

        tasks.append(plot_generic(dirname, 'minutes_for_trajectory', 'Update Number', r'Minutes', 'Time for Trajectory'))

        tasks.append(plot_generic(dirname, 'n_steps', 'Update Number', r'Step Count (coarsest time scale)', 'Integration Steps'))
        #tasks.append(plot_generic(dirname, 'n_steps-vs-md_time', 'MD Time', r'Step Count (coarsest time scale)', 'Integration Steps'))

        tasks.append(plot_generic(dirname, 'md_time', 'Update Number', r'MD Time', 'MD Distance'))
        tasks.append(plot_generic(dirname, 'tau0', 'Update Number', r'MD Step Size', 'MD Step Size'))

        tasks.append(plot_generic(dirname, 'DeltaDeltaH', 'Update Number', r'$\Delta \Delta H$', 'Reversibility'))
        tasks.append(plot_generic(dirname, 'DeltaDeltaH_over_DeltaH', 'Update Number', r'$\Delta \Delta H / \Delta H$', 'Reversibility'))

        tasks.append(plot_generic(dirname, 'exp_deltaH', 'Update Number', r'$\exp(-\Delta H)$', 'MD EnergeReversibility'))

        tasks.append(plot_generic(dirname, 't0', 'Update Number', r'$t_0$', 'Wilson Flow Scale Setting'))
        tasks.append(plot_generic(dirname, 'w0', 'Update Number', r'$w_0$', 'Wilson Flow Scale Setting'))

        tasks.append(plot_generic(dirname, 'AcceptP', 'Update Number', r'Accepted', 'Acceptance Rate'))
        tasks.append(plot_generic(dirname, 'AcceptP-running_mean_100', 'Update Number', r'Running mean (100 step window)', 'Acceptance Rate'))

        path_out = names.tsv_extract(dirname, 'AcceptP-running_mean_100')

    for task in tasks:
        for subtask in task:
            yield subtask


def task_correlators():
    for dirname in directories:
        for meson in ['pion', 'kaon']:
            corr_tsv_files = []
            for corr_xml in glob.glob(os.path.join(dirname, 'corr', 'corr.config-*.{}.xml'.format(meson))):
                corr_tsv = names.correlator_tsv(corr_xml, meson)
                corr_tsv_files.append(corr_tsv)
                yield make_single_transform(dirname,
                                            correlators.io_extract_pion_corr,
                                            corr_xml,
                                            corr_tsv)
            
            if len(corr_tsv_files) > 0:
                path_pion_mass = names.tsv_extract(dirname, meson + '_mass')
                yield {
                    'actions': [(correlators.analysis.io_extract_mass, [corr_tsv_files, path_pion_mass])],
                    'name': path_pion_mass,
                    'file_dep': corr_tsv_files,
                    'targets': [path_pion_mass],
                }

                path_effective_mass = names.tsv_extract(dirname, meson + '_effective_mass')
                yield {
                    'actions': [(correlators.analysis.io_effective_mass, [corr_tsv_files, path_effective_mass])],
                    'name': path_effective_mass,
                    'file_dep': corr_tsv_files,
                    'targets': [path_effective_mass],
                }


def task_running_mean():
    for dirname in directories:
        path_in = names.tsv_extract(dirname, 'AcceptP')
        path_out = names.tsv_extract(dirname, 'AcceptP-running_mean_100')
        yield make_single_transform(dirname,
                                    transforms.io_running_mean,
                                    path_in,
                                    path_out)
