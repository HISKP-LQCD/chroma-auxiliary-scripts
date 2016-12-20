#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import pprint
import textwrap

from pyparsing import Word, Optional, OneOrMore, Group, ParseException, Suppress, SkipTo, ZeroOrMore, Combine

caps = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
lowers = caps.lower()
digits = "0123456789"


def print_results(results):
    lines = []
    #lines.append(str(type(results)))
    if isinstance(results, str):
        lines.append(results)
    else:
        for key, val in sorted(results.items()):
            lines.append(key)
            lines.append(textwrap.indent(print_results(val), '  '))

    return '\n'.join(lines)



def main(options):
    pp = pprint.PrettyPrinter()

    with open(options.logfile) as f:
        content = f.read()

    all_letters = ''.join(sorted(set(content)))

    g_integer = Word(digits)
    g_float = Word(digits + '+-.eE')

    g_subgrid_volume = Suppress('subgrid volume =') + g_integer('subgrid_volume')

    g_invcg = Combine(Suppress('QDP:FlopCount:invcg2 Performance/CPU: t=')
                      + Suppress(g_float)
                      + Suppress('(s) Flops=')
                      + Suppress(g_float)
                      + Suppress(' => ')
                      + Suppress(g_float)
                      + Suppress(' Mflops/cpu.\nQDP:FlopCount:invcg2 Total performance:  ')
                      + Suppress(g_float)
                      + Suppress(' Mflops = ')
                      + g_float('gflops')
                      + Suppress(' Gflops = ')
                      + Suppress(g_float)
                      + Suppress(' Tflops\nCG_SOLVER: ')
                      + g_integer('iterations')
                      + Suppress(' iterations. Rsd = ')
                      + Suppress(g_float)
                      + Suppress(' Relative Rsd = ')
                      + Suppress(g_float)
                      + Suppress('\nCG_SOLVER_TIME: ')
                      + Suppress(g_float)
                      + Suppress(' sec')
                     )
    #g_invcg = g_float('gflops') + Suppress('Gflops = ')

    g_update = Suppress('Doing Update:') + g_integer('update_no')
    g_before_update = SkipTo(g_update)
    g_solver_block = g_invcg('invcg')
    g_solver_blocks = Suppress(SkipTo(g_solver_block)) + g_solver_block
    g_update_block = Suppress(g_before_update) + Group(g_update + OneOrMore(g_solver_blocks))('update_block')
    g_logfile = Suppress(SkipTo(g_subgrid_volume)) + g_subgrid_volume + OneOrMore(g_update_block)

    results = g_logfile.parseString(content)

    print(print_results(results))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('logfile')

    options = parser.parse_args()
    main(options)


if __name__ == '__main__':
    _parse_args()
