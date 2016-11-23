#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import multiprocessing
import os
import pprint
import shlex
import subprocess


def quote_words(words):
    mapped = list(map(shlex.quote, words))
    joined = ' '.join(mapped)
    return joined

def quote_quoted_words(words):
    return shlex.quote(quote_words(words))


pp = pprint.PrettyPrinter()


standout_enter = subprocess.check_output(['tput', 'setaf', '3']).decode().strip()
standout_exit = subprocess.check_output(['tput', 'sgr0']).decode().strip()


class Flags(object):
    def __init__(self, parents=[], common=[], c=[], cxx=[], configure=[]):
        self.flags = {
            'common': common,
            'c': c,
            'cxx': cxx,
            'configure': configure,
        }
        self.parents = parents

    def get_flags(self, kind):
        result = []
        for parent in self.parents:
            result += parent.get_flags(kind)
        result += self.flags[kind]
        return result

    @property
    def c(self):
        return quote_words(self.get_flags('c') + self.get_flags('common'))

    @property
    def cxx(self):
        return quote_words(self.get_flags('cxx') + self.get_flags('common'))

    @property
    def configure(self):
        return self.get_flags('configure') + [
            'CFLAGS={}'.format(shlex.quote(self.c)),
            'CXXFLAGS={}'.format(shlex.quote(self.cxx)),
        ]


common = Flags(
    common=['-O2', '-finline-limit=50000', '-fopenmp'],
    c= [ '--std=c99'],
    cxx= ['--std=c++11'],
    configure = [
        #'CXX=/usr/bin/g++',
        #'CC=/usr/bin/gcc',
    ],
)

jureca = Flags(
    parents = [common],
    common = ['-msse', '-march=native'],
    configure = [
        '--enable-sse',
        '--enable-sse2',
    ]
)

juqueen = Flags(parents=[common])

qdpxx = Flags(
    configure=[
        '--enable-openmp',
    ],
)

chroma = Flags(
    configure=[
        '--with-gmp=/usr/include/',
        '--with-qdp=../qdpxx',
        '--enable-openmp',
    ],
)

juqueen_qmp = Flags(
    parents=[juqueen],
    configure=[
        '--enable-bgq',
        '--enable-bgspi',
        #'--with-qmp-comms-type=MPI',
    ],
)

juqueen_qdpxx = Flags(
    parents=[juqueen, qdpxx],
    configure=[
        '--enable-parallel-arch=parscalar',
        '--with-qmp=../qmp',
    ],
)

juqueen_chroma = Flags(
    parents=[juqueen, chroma],
    configure=[
        '--with-qmp=../qmp',
    ]
)


def print_command(command):
    print()
    #print(standout_enter, end='')
    print(os.path.basename(os.getcwd()))
    pp.pprint(command)
    #print(quote_words(command), end='')
    #print(standout_exit, end='')


def print_check_call(command, *args, **kwargs):
    print_command(command)
    if not options.dry:
        if options.confirm:
            input('Please press Enter to proceed ...')
        subprocess.check_call(command, *args, **kwargs)


def build_project(directory, flags):
    old_cwd = os.getcwd()
    os.chdir(directory)

    if not os.path.isfile('configure') or options.dry:
        print_check_call(['./autogen.sh'])

    if not os.path.isfile('Makefile') or options.dry:
        print_check_call(['./configure'] + flags.configure)

    if not os.path.isfile('build-succeeded') or options.dry:
        print_check_call([
            'nice', 'make', '-j', str(multiprocessing.cpu_count()),
            'CFLAGS={}'.format(flags.c),
            'CXXFLAGS={}'.format(flags.cxx),
        ])

        if not options.dry:
            with open('build-succeeded', 'w') as f:
                f.write('done')

    os.chdir(old_cwd)


def clone_if_needed(url, directory, branch=None):
    if os.path.isdir(directory) and not options.dry:
        return

    command = ['git', 'clone', '--recursive', url, directory]
    if branch is not None:
        command += ['-b', branch]

    print_check_call(command)



def main():
    _parse_args()

    clone_if_needed('https://github.com/usqcd-software/qmp', 'qmp')
    clone_if_needed('https://github.com/martin-ueding/qdpxx.git', 'qdpxx', 'martins-fedora24-build')
    clone_if_needed('https://github.com/martin-ueding/chroma.git', 'chroma', 'submodules-via-https')

    build_project('qmp', juqueen_qmp)
    build_project('qdpxx', juqueen_qdpxx)
    build_project('chroma', juqueen_chroma)


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('--confirm', action='store_true')
    global options
    options = parser.parse_args()


if __name__ == '__main__':
    main()
