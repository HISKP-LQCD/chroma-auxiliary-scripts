#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import pprint

from lxml import etree
import yaml


def python_to_tree(p):
    assert isinstance(p, dict)

    key_val = list(p.items())

    assert len(key_val) == 1

    key, value = key_val[0]
    e = etree.Element(key)
    if isinstance(value, str):
        e.text = value
    elif isinstance(value, list):
        for item in reversed(value):
            i = python_to_tree(item)
            e.insert(0, i)
    else:
        raise RuntimeError('Value of dict element must be either str or list.')

    return e


def main():
    options = _parse_args()

    with open(options.yml_file) as f:
        y = yaml.load(f.read())

    tree = python_to_tree(y)

    with open(options.xml_file, 'wb') as f:
        f.write(etree.tostring(tree, xml_declaration=True, pretty_print=True, encoding='utf-8'))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('yml_file')
    parser.add_argument('xml_file')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
