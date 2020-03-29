#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <mu@martin-ueding.de>

import argparse
import re

pattern = re.compile(r'#ifndef (.*)\n#define \1\n')

def main():
    options = _parse_args()

    for filename in options.files:
        normalize_file(filename)

def normalize_file(filename):
    with open(filename) as f:
        contents = f.read()

    m = pattern.search(contents)
    if m:

        new_guard_var = re.sub(r'\W', '_', filename.upper())

        print(m.group(1), new_guard_var)

        new_contents = pattern.sub('#ifndef {0}\n#define {0}\n'.format(new_guard_var), contents)

        with open(filename, 'w') as f:
            f.write(new_contents)

def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('files', nargs='+')
    options = parser.parse_args()

    return options

if __name__ == '__main__':
    main()
