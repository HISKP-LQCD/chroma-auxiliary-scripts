#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

import argparse

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op
from scipy.interpolate import interp1d

import util
import wflow


def main():
    options = _parse_args()

    fig, ax = util.make_figure()

    t, e = util.load_columns('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit//Runs/0106-bmw-rho011/shard-wflow.config-100.out.xml.e.tsv')
    t, w = util.load_columns('/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit//Runs/0106-bmw-rho011/shard-wflow.config-100.out.xml.w.tsv')

    data = np.loadtxt('gradflow.000100', skiprows=1)

    tm_traj = data[:, 0]
    tm_t = data[:, 1]
    tm_P = data[:, 2]
    tm_Eplaq = data[:, 3]
    tm_Esym = data[:, 4]
    tm_tsqEplaq = data[:, 5]
    tm_tsqEsym = data[:, 6]
    tm_Wsym = data[:, 7]

    for i, method in enumerate(['gradient', 'chain-gradient', 'explicit-sym', 'explicit-asym']):
        tm_my_w = wflow.derive_w(tm_t, tm_Esym, method=method)
        ax.plot(tm_t + 0.1*i, np.abs(tm_Wsym - tm_my_w), label=method)

    ax.set_yscale('log')
    ax.set_xlabel('$t/a^2$ (shifted)')
    ax.set_ylabel(r'$\left|(w/a)^\mathrm{tmLQCD} - (w/a)^\mathrm{Method}\right|$')
    util.save_figure(fig, 'plot-wflow-norm')


    x = np.linspace(0, 4, 1000)
    y = np.sin(x)
    z = x * (x**2 * np.cos(x) + 2 * x * np.sin(x))
    fig, ax = util.make_figure()
    for i, method in enumerate(['gradient', 'chain-gradient', 'explicit-sym', 'explicit-asym']):
        w = wflow.derive_w(x, y, method=method)
        ax.plot(x + 0.1*i, np.abs(z - w), label=method)
    ax.set_xlabel('$x$ (shifted)')
    ax.set_ylabel('absolute deviation from analytic $w(x)$')
    ax.set_yscale('log')
    util.save_figure(fig, 'plot-gradient-check')
    

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
