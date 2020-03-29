#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016-2017 Martin Ueding <mu@martin-ueding.de>

import argparse
import itertools
import pprint
import re
import os
import subprocess

git_grep_pattern = re.compile(r'([^:]+):\s*const std::string name.*"([^"]+)".*;')


def main():
    options = _parse_args()

    lines = subprocess.check_output(['git', 'grep', 'const std::string name']).decode().strip().split('\n')

    data = {}

    for line in lines:
        m = git_grep_pattern.search(line)
        if m:
            path = m.group(1)
            name = m.group(2)
            bits = os.path.dirname(path).split('/')

            enter(data, bits, name)

    pp = pprint.PrettyPrinter()
    pp.pprint(data)

    format_as_dot(data, 'chroma-names-leaves.dot', True)
    format_as_dot(data, 'chroma-names-trunk.dot', False)

    format_as_tikz(data, 'chroma-names-leaves.tex', True)
    format_as_tikz(data, 'chroma-names-trunk.tex', False)

    format_as_latex(data, 'chroma-names-list.tex')
    format_as_markdown(data, 'chroma-names-list.md')


def enter(data, bits, name):
    it = data
    for bit in bits + [name]:
        if not bit in it:
            it[bit] = {}
        it = it[bit]


def format_as_dot(data, filename, leaves=True):
    with open(filename, 'w') as f:
        f.write('''digraph {
            overlap = false;
            rankdir = LR;
            ''')
        f.write('\n'.join(_format_as_dot(data, leaves=leaves)))
        f.write('\n}')


def get_prefix_key(prefix, key):
    return (prefix + 'x' + key).replace('_', 'x')


def unique(data):
    return list(set(data))


def _format_as_dot(subtree, prefix='', leaves=True):
    lines = []
    for key, vals in sorted(subtree.items()):

        prefix_key = get_prefix_key(prefix, key)

        if leaves or len(vals.keys()) != 0:
            lines.append('"{}" [label="{}"{}];'.format(
                prefix_key,
                key,
                'shape=box' if len(vals.keys()) == 0 else '',
            ))

        for key2, val2 in sorted(vals.items()):
            if leaves or len(val2.keys()) != 0:
                lines.append('"{}" -> "{}";'.format(prefix_key, get_prefix_key(prefix_key, key2)))

        if not leaves and len(vals.keys()) == 0:
            continue

        lines += _format_as_dot(vals, prefix_key, leaves)

    return lines


def format_as_tikz(data, filename, leaves):
    with open(filename, 'w') as f:
        f.write(r'''\begin{tikzpicture}
    \graph[branch down=2cm, grow right sep=1cm] {
''')
        f.write('\n'.join(indent(_format_as_tikz(data, leaves=leaves), 2)))
        f.write('''
    };
\end{tikzpicture}''')


def _format_as_tikz(subtree, prefix='', leaves=True, level=3):
    lines = []
    for key, val in sorted(subtree.items()):
        prefix_key = get_prefix_key(prefix, key)
        escaped = key.replace('_', r'\_')
        if len(val.keys()) == 0:
            #lines.append('{}/"{}",'.format(prefix_key, escaped))
            lines.append('{},'.format(prefix_key))
        else:
            #lines.append('{}/"{}" -> {{'.format(prefix_key, escaped))
            lines.append('{} -> {{'.format(prefix_key))
            lines += indent(_format_as_tikz(val, prefix_key))
            lines.append('},')

    return lines


def format_as_latex(subtree, filename):
    results = _format_as_latex(subtree)
    with open(filename, 'w') as f:
        for key, vals in sorted(results.items()):
            f.write(r'\needspace{8\baselineskip}' + '\n')
            f.write(r'\textbf{' + key[len('/lib'):].replace('_', r'\_\-') + '}\n')
            maxlen = max(len(val) for val in vals)
            threshold = 31
            if maxlen < threshold:
                f.write(r'\begin{multicols}{2}' + '\n')
            f.write(r'\begin{itemize}[noitemsep]' + '\n')
            for val in sorted(vals):
                f.write(r'\item \texttt{' + val.replace('_', r'\_') + '}\n')
            f.write(r'\end{itemize}' + '\n\n')
            if maxlen < threshold:
                f.write(r'\end{multicols}' + '\n')



def _format_as_latex(subtree, prefix='', leaves=True):
    results = {}
    for key, val in sorted(subtree.items()):
        prefix_key = prefix + '/' + key
        escaped = key.replace('_', r'\_')
        if len(val.keys()) == 0:
            if not prefix in results:
                results[prefix] = []
            results[prefix].append(key)
        else:
            results.update(_format_as_latex(val, prefix_key))

    return results


def format_as_markdown(subtree, filename):
    results = _format_as_markdown(subtree)
    with open(filename, 'w') as f:
        for key, vals in sorted(results.items()):
            f.write(r'**' + key[len('/lib'):] + '**\n\n')
            for val in sorted(vals):
                f.write(r'- ' + val + '\n')
            f.write('\n')



def _format_as_markdown(subtree, prefix='', leaves=True):
    results = {}
    for key, val in sorted(subtree.items()):
        prefix_key = prefix + '/' + key
        if len(val.keys()) == 0:
            if not prefix in results:
                results[prefix] = []
            results[prefix].append(key)
        else:
            results.update(_format_as_markdown(val, prefix_key))

    return results


def indent(lines, level=1):
    return ['    '*level + line for line in lines]


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
