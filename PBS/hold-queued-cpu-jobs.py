#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>
# Licensed under the MIT/Expat license.

import argparse
import os
import subprocess
import xml.etree.ElementTree as ET


def main():
    options = _parse_args()

    qstat_xml = subprocess.check_output(['qstat', '-x'])

    tree = ET.fromstring(qstat_xml)
    root = tree

    my_cpu_jobs = []

    for job in root.findall('.//Job'):
        job_id = job.find('Job_Id').text
        job_state = job.find('job_state').text
        job_name = job.find('Job_Name').text
        job_owner = job.find('Job_Owner').text

        # Skip other people's jobs.
        if not job_owner.startswith(options.user):
            continue

        if job_state == {'hold': 'Q', 'release': 'H'}[options.action]:
            nodes = job.findall('Resource_List/nodes')
            is_cpu_job = True
            for node in nodes:
                words = node.text.split(':')
                if any(word.startswith('gpus=') for word in words):
                    is_cpu_job = False


            if is_cpu_job:
                my_cpu_jobs.append((job_id, job_name))

    if len(my_cpu_jobs) == 0:
        print('No jobs founds.')
        return

    print('Found the following jobs that do not use GPUs and are in state “Q”:')
    for job_id, job_name in sorted(my_cpu_jobs):
        print('- {} {}'.format(job_id, job_name))
    print()

    commands = []

    for job_id, job_name in sorted(my_cpu_jobs):
        command = []
        if options.action == 'hold':
            command.append('qhold')
        elif options.action == 'release':
            command.append('qrls')
        command.append(str(job_id))
        commands.append(command)

    print('The following commands will be executed:')
    for command in commands:
        print(' '.join(command))
    print()

    if options.armed:
        for command in commands:
            print(' '.join(command))
            subprocess.check_call(command)
    else:
        print('Nothing has been done. Run the script again with `--armed` in order to actually perform the actions.')


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='Holds or releases all PBS jobs that do not use GPUs.')
    parser.add_argument('action', choices=['hold', 'release'])
    parser.add_argument('--armed', action='store_true', help='Actually change the job states')
    parser.add_argument('--user', default=os.getlogin(), help='Username. Default: %(default)s')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
