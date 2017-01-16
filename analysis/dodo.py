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
        for logfile in glob.glob(os.path.join(directory, 'hmc.slurm-*.out.txt')):
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
        for converter, outname in [(transforms.gflops_per_node_converter, 'gflops_per_node'), (transforms.iteration_converter, 'iters'), (transforms.residual_converter, 'residuals')]:
            yield {
                'actions': [(transforms.convert_solver_list, [directory, converter, outname])],
                'name': directory + '/' + outname,
                'file_dep': [names.log_extract(directory)],
                'targets': [],
            }


def task_xpath_shards():
    for directory in directories:
        for key, extractor in extractors.xmlfile.bits.items():
            shard_names = []
            for xml_file in itertools.chain(glob.glob(os.path.join(directory, 'hmc.slurm-*.out.xml')),
                                            glob.glob(os.path.join(directory, 'hmc.slurm-*.log.xml'))):
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
        yield make_single_transform(dirname,
                                    transforms.convert_tau0_to_md_time,
                                    os.path.join(dirname, 'extract-tau0.tsv'),
                                    os.path.join(dirname, 'extract-md_time.tsv'))

def task_wflow():
    for dirname in directories:
        files_t0 = []
        files_w0 = []

        for xml_file in glob.glob(os.path.join(dirname, 'wflow.config-*.out.xml')):
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
    return {
        'actions': [(visualizers.plot_generic, [[dirname], name] + list(args), kwargs)],
        'name': dirname + '/' + name,
        'file_dep': [os.path.join(dirname, 'extract', 'extract-{}.tsv'.format(name))],
        'targets': [names.plot(dirname, name)],
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


def task_correlators():
    for dirname in directories:
        corr_tsv_files = []
        for corr_xml in glob.glob(os.path.join(dirname, 'corr.config-*.out.xml')):
            corr_tsv = names.correlator_tsv(corr_xml)
            corr_tsv_files.append(corr_tsv)
            yield make_single_transform(dirname,
                                        correlators.io_extract_pion_corr,
                                        corr_xml,
                                        corr_tsv)
        
        if len(corr_tsv_files) > 0:
            path_pion_mass = names.pion_mass(dirname)
            yield {
                'actions': [(correlators.analysis.io_extract_mass, [corr_tsv_files, path_pion_mass])],
                'name': dirname,
                'file_dep': corr_tsv_files,
                'targets': [path_pion_mass],
            }
