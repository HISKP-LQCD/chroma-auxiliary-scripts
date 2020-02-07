#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <martin-ueding.de>
# Licensed under the MIT license.

import argparse
import pprint
import re


type_pattern = re.compile(r'Construct (\w+) rational approx= REMEZ')
coeff_pattern = re.compile(r'pfe: Residue = ([0-9.e+-]+) Pole = ([0-9.e+-]+)')
norm_pattern = re.compile(r'root: Normalisation constant is ([0-9.e+-]+)')



def get_coeff(lines):
    results = {'action': [], 'force': []}
    norms = {'action': None, 'force': None}

    for line in lines:
        m = type_pattern.match(line)
        if m:
            type_ = m.group(1)

        m = coeff_pattern.match(line)
        if m:
            residue, pole = m.groups()
            results[type_].append((residue, pole))

        m = norm_pattern.match(line)
        if m:
            norm = m.group(1)
            norms[type_] = norm

    return results, norms


def full_to_xml_lines(norms, coeffs):
    result = []

    result.append('<!-- action -->')
    result += coeff_to_xml_lines(norms['action'], coeffs['action'])
    result.append('<!-- force -->')
    result += coeff_to_xml_lines(norms['force'], coeffs['force'])

    return result


def coeff_to_xml_lines(norm, coeffs):
    coeff_count = len(coeffs)
    half = coeff_count // 2

    result = []
    result.append('<PFECoeffs>')
    result += single_to_xml_lines(str(1/float(norm)), coeffs[:half])
    result.append('</PFECoeffs>')
    result.append('<IPFECoeffs>')
    result += single_to_xml_lines(norm, coeffs[half:])
    result.append('</IPFECoeffs>')

    return result


def single_to_xml_lines(norm, coeffs):
    residues, poles = zip(*coeffs)

    result = []
    result.append('<norm>{}</norm>'.format(norm))
    result.append('<res>{}</res>'.format(' '.join(residues)))
    result.append('<pole>{}</pole>'.format(' '.join(poles)))

    return result


def main():
    options = _parse_args()

    with open(options.hmc_output) as f:
        lines = f.readlines()

    results, norms = get_coeff(lines)

    pp = pprint.PrettyPrinter()
    pp.pprint(results)

    print('\n'.join(full_to_xml_lines(norms, results)))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('hmc_output')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
