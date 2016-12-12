#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

import argparse
import os
import pprint
import subprocess

from lxml import etree
import jinja2
import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op

template_text = r'''
\documentclass[a3paper, landscape, DIV=100]{scrartcl}
\pagestyle{empty}
\usepackage{tikz}
\begin{document}
    \begin{tikzpicture}
        %< set ticks = 100 >%
        %< set x_stretch = 150 >%
        %< set num_mon = monomials|length >%
        %< for i in range(ticks) >%
        \draw (<< x_stretch * i / ticks >>, -0.5) -- ++(0, << num_mon >>) node[above] {$<< i / ticks >>$};
        %< endfor >%
        %< for i in range(10) >%
        \draw[thick, red] (<< x_stretch * i / 10 >>, -0.5) -- ++(0, << num_mon >>);
        %< endfor >%
        %< for monomial, evaluations in monomials >%
        %< set y = loop.index0 >%
        \node[anchor=east] at (-1, << y >>) {\texttt{<< translation[monomial] >>}};
        %< for evaluation in evaluations >%
        \draw[fill] (<< x_stretch * evaluation >>, << y >>) circle (0.05);
        %< endfor >%
        %< endfor >%
    \end{tikzpicture}
\end{document}
'''


def main():
    options = _parse_args()

    pp = pprint.PrettyPrinter()

    print('Loading XML …')
    tree = etree.parse(options.xml_file)

    print('Extracting first update …')
    steps = tree.xpath('/hmc/doHMC/MCUpdates/elem')
    print(steps)
    step = steps[0]

    print('Extracting forces …')
    leaps = step.xpath('Update/HMCTrajectory/leapP')
    t = {}
    evaluations = {}
    for leap in leaps:
        dt = float(leap.xpath('dt/text()')[0])

        monomials = leap.xpath('AbsHamiltonianForce/ForcesByMonomial/elem/*')
        tags = [monomial.tag for monomial in monomials]

        used = []
        for tag in tags:
            if not tag in t:
                t[tag] = 0.0
                evaluations[tag] = []

            if tag not in used:
                used.append(tag)
                t[tag] += dt
                evaluations[tag].append(t[tag])

                print(t[tag], tag)

    pp.pprint(evaluations)

    env = jinja2.Environment(
        "%<", ">%",
        "<<", ">>",
        "[§", "§]",
        loader=jinja2.FileSystemLoader(".")
    )
    template = env.from_string(template_text)

    translation = {
        'TwoFlavorExactRatioConvConvWilsonTypeFermMonomial': 'light-det-ratio',
        'EvenOddPrecLogDetEvenEvenMonomial': 'light-logdet',
        'OneFlavorRatExactWilsonTypeFermMonomial': 'strange-det',
        'GaugeMonomial': 'gauge',
        'TwoFlavorExactWilsonTypeFermMonomial': 'light-det',
    }

    rendered = template.render(monomials=sorted(evaluations.items()), translation=translation)
    with open('evaluations.tex', 'w') as f:
        f.write(rendered)

    subprocess.check_call(['lualatex', '--halt-on-error', 'evaluations.tex'])

    print(repr(evaluations.keys()))


def _parse_args():
    '''
    Parses the command line arguments.

    :return: Namespace with arguments.
    :rtype: Namespace
    '''
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('xml_file')
    options = parser.parse_args()

    return options


if __name__ == '__main__':
    main()
