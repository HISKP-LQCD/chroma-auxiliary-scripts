#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import glob

import numpy as np

import util


def load_average_corr(paths):
    t = util.load_columns(paths[0])[0]
    reals = [util.load_columns(path)[1] for path in paths]
    a = np.row_stack(reals)
    return t, np.mean(a, axis=0), np.std(a, axis=0) / np.sqrt(len(reals))

source_0 = load_average_corr(glob.glob('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/Runs/0120-Mpi270-L24-T96/corr/T=0/extract/corr/*.tsv'))
source_20 = load_average_corr(glob.glob('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/Runs/0120-Mpi270-L24-T96/corr/extract/corr/*.tsv'))

fig, ax = util.make_figure()

print([x.shape for x in source_0])

ax.errorbar(source_0[0], source_0[1], source_0[2], label='T = 0')
ax.errorbar(source_20[0], source_20[1], source_20[2], label='T = 20')
ax.set_title('Different Source time with Chroma')
ax.set_xlabel(r'$t$')
ax.set_ylabel(r'$C(t)$')
ax.set_yscale('log')

util.save_figure(fig, 'chroma-source_t20')
