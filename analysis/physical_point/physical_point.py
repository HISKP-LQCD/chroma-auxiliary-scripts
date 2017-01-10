#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import argparse
import itertools

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op
from unitprint import siunitx

import bootstrap
import util


def gmor(a_m_ud, c_1, c_2):
    return c_1 * (a_m_ud + c_2)


def main():
    options = _parse_args()
    R = 1000

    a_inv_val = 1616
    a_inv_err = 20
    a_inv_dist = bootstrap.make_dist(a_inv_val, a_inv_err, n=R)

    a_m_ud, a_m_s, l, t, trajectories, a_m_pi_val, a_m_pi_err, a_m_k_val, a_m_k_err, f_k_f_pi_val, f_k_f_pi_err = util.load_columns('physical_point/gmor.txt')
    a_m_pi_dist = bootstrap.make_dist(a_m_pi_val, a_m_pi_err, n=R)

    x = a_m_ud
    m_pi_sq_dist = [
        (a_inv * a_m_pi)**2
        for a_inv, a_m_pi in zip(a_inv_dist, a_m_pi_dist)]
    m_pi_dist = [
        np.sqrt(m_pi)
        for m_pi in m_pi_sq_dist]

    popt_dist = [
        op.curve_fit(gmor, x, m_pi_sq)[0]
        for m_pi_sq in m_pi_sq_dist]

    phys_dist = [
        op.newton(lambda a_m: gmor(a_m, *popt) - 135**2, np.min(x))
        for popt in popt_dist]

    fit_x = np.linspace(np.min(phys_dist), np.max(x), 100)
    fit_y_dist = [
        np.sqrt(gmor(fit_x, *popt))
        for popt in popt_dist]

    phys_cen, phys_val, phys_err = bootstrap.average_and_std_arrays(phys_dist)
    fit_y_cen, fit_y_val, fit_y_err = bootstrap.average_and_std_arrays(fit_y_dist)
    m_pi_cen, m_pi_val, m_pi_err = bootstrap.average_and_std_arrays(m_pi_dist)

    print(siunitx(phys_cen, phys_err))

    fig = pl.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.fill_between(fit_x, fit_y_val - fit_y_err, fit_y_val + fit_y_err, color='0.8')
    ax.plot(fit_x, fit_y_val, color='black', label='GMOR Fit')
    ax.errorbar(x, m_pi_val, yerr=m_pi_err, color='blue', marker='+', linestyle='none', label='Data')
    ax.errorbar([phys_cen], [135], xerr=[phys_err], marker='+', color='red', label='Extrapolation')
    ax.set_title('Extrapolation to the Physical Point')
    ax.set_xlabel(r'$a m_\mathrm{ud}$')
    ax.set_ylabel(r'$M_\pi / \mathrm{MeV}$')
    util.dandify_axes(ax)

    ax = fig.add_subplot(2, 1, 2)
    ax.hist(phys_dist - phys_cen, bins=50)
    ax.locator_params(nbins=6)
    ax.set_title('Bootstrap Bias')
    ax.set_xlabel(r'$(a m_\mathrm{ud}^\mathrm{phys})^* - a m_\mathrm{ud}^\mathrm{phys}$')
    util.dandify_axes(ax)

    util.dandify_figure(fig)
    fig.savefig('GMOR.pdf')


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
