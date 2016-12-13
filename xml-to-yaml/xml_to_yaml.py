#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import pprint

from lxml import etree
import yaml


def tree_to_python(tree):
    if isinstance(tree, str):
        return tree
    elif isinstance(tree, etree._Comment):
        return None
    elif len(tree.getchildren()) == 0:
        return {tree.tag: tree.text}
    else:
        converted = [tree_to_python(child) for child in tree.iterchildren()]
        return {tree.tag: [c for c in converted if c is not None]}


def main():
    options = _parse_args()

    tree = etree.parse(options.xml_file)
    root = tree.getroot()
    pp = pprint.PrettyPrinter()
    p = tree_to_python(root)
    y = yaml.dump(p, default_flow_style=False)

    with open(options.yml_file, 'w') as f:
        f.write(y)


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('xml_file')
    parser.add_argument('yml_file')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
