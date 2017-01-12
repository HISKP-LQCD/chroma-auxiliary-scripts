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
                'name': logfile,
                'file_dep': [logfile],
                'targets': [shard_name],
            }

        merged_name = os.path.join(directory, 'extract-log.json')

        yield {
            'actions': [(transforms.merge_json_shards, [shard_names, merged_name])],
            'name': merged_name,
            'file_dep': shard_names,
            'targets': [merged_name],
        }
