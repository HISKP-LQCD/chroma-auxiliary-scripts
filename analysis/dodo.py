#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import glob
import os

import extractors
import transforms

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
            for xml_file in glob.glob(os.path.join(directory, 'hmc.slurm-*.out.xml')):
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


