#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import os

import extractors

os.chdir('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/Runs')

directories = list(filter(os.path.isdir, os.listdir()))


def task_extract_from_xmlfile():
    for directory in directories:
        yield {
            'actions': [lambda task: extractors.xmlfile.process_directory(task.file_dep[0])],
            'name': directory,
            'targets': [directory],
        }
