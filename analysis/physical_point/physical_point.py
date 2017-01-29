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

try:
    from unitprint import siunitx
except ImportError:
    siunitx = lambda *kw: ' '.join(map(str, kw))


def gmor_pion(aml, aB, aml_cr):
    return 2 * aB * (aml + aml_cr)


def main():
    options = _parse_args()
    R = 1000

    # Read in the data from the paper.
    a_inv_val = 1616
    a_inv_err = 20
    a_inv_dist = bootstrap.make_dist(a_inv_val, a_inv_err, n=R)
    aml, ams, l, t, trajectories, ampi_val, ampi_err, amk_val, amk_err, f_k_f_pi_val, f_k_f_pi_err = util.load_columns('physical_point/gmor.txt')
    ampi_dist = bootstrap.make_dist(ampi_val, ampi_err, n=R)
    amk_dist = bootstrap.make_dist(amk_val, amk_err, n=R)

    # Convert the data in lattice units into physical units.
    mpi_dist = [a_inv * ampi for ampi, a_inv in zip(ampi_dist, a_inv_dist)]
    mpi_val, mpi_avg, mpi_err = bootstrap.average_and_std_arrays(mpi_dist)
    mpi_sq_dist = [mpi**2 for mpi in mpi_dist]
    mpi_sq_val, mpi_sq_avg, mpi_sq_err = bootstrap.average_and_std_arrays(mpi_sq_dist)
    ampi_sq_dist = [ampi**2 for ampi in ampi_dist]
    ampi_sq_val, ampi_sq_avg, ampi_sq_err = bootstrap.average_and_std_arrays(ampi_sq_dist)

    # Do a GMOR fit in order to extract `a B` and `a m_cr`.
    popt_dist = [op.curve_fit(gmor_pion, aml, ampi_sq)[0]
                 for ampi_sq in ampi_sq_dist]
    aB_dist = [popt[0] for popt in popt_dist]
    amcr_dist = [popt[1] for popt in popt_dist]
    aB_val, aB_avg, aB_err = bootstrap.average_and_std_arrays(aB_dist)
    amcr_val, amcr_avg, amcr_err = bootstrap.average_and_std_arrays(amcr_dist)
    print('aB =', siunitx(aB_val, aB_err))
    print('am_cr =', siunitx(amcr_val, amcr_err))

    # Physical meson masses from FLAG paper.
    mpi_phys_dist = bootstrap.make_dist(134.8, 0.3, R)
    mk_phys_dist = bootstrap.make_dist(494.2, 0.3, R)
    ampi_phys_dist = [mpi_phys / a_inv
                      for a_inv, mpi_phys in zip(a_inv_dist, mpi_phys_dist)]
    amk_phys_dist = [mk_phys / a_inv
                     for a_inv, mk_phys in zip(a_inv_dist, mk_phys_dist)]
    ampi_phys_val, ampi_phys_avg, ampi_phys_err = bootstrap.average_and_std_arrays(ampi_phys_dist)
    amk_phys_val, amk_phys_avg, amk_phys_err = bootstrap.average_and_std_arrays(amk_phys_dist)
    print('aM_pi phys =', siunitx(ampi_phys_val, ampi_phys_err))
    print('aM_k phys =', siunitx(amk_phys_val, amk_phys_err))

    # Compute the strange quark mass that is needed to obtain a physical meson
    # mass difference, ignoring lattice artifacts.
    ams_phys_dist = [
        (amk_phys**2 - 0.5 * ampi_phys**2) / aB - amcr
        for ampi_phys, amk_phys, aB, amcr in zip(ampi_phys_dist, amk_phys_dist, aB_dist, amcr_dist)]
    ams_phys_cen, ams_phys_val, ams_phys_err = bootstrap.average_and_std_arrays(ams_phys_dist)
    print('M_K = {} MeV <== am_s ='.format(siunitx(494.2, 0.3)), siunitx(ams_phys_cen, ams_phys_err))
    aml_phys_dist = [op.newton(lambda aml: gmor_pion(aml, *popt) - ampi_phys**2, np.min(aml))
                     for popt, ampi_phys in zip(popt_dist, ampi_phys_dist)]

    fit_x = np.linspace(np.min(aml_phys_dist), np.max(aml), 100)
    fit_y_dist = [np.sqrt(gmor_pion(fit_x, *popt)) * a_inv
                  for popt, a_inv in zip(popt_dist, a_inv_dist)]
    fit_y_cen, fit_y_val, fit_y_err = bootstrap.average_and_std_arrays(fit_y_dist)

    np.savetxt('physical_point/mpi-vs-aml-data.tsv',
               np.column_stack([aml, mpi_val, mpi_err]))
    np.savetxt('physical_point/mpi-vs-aml-fit.tsv',
               np.column_stack([fit_x, fit_y_cen]))
    np.savetxt('physical_point/mpi-vs-aml-band.tsv',
               bootstrap.pgfplots_error_band(fit_x, fit_y_cen, fit_y_err))

    aml_phys_val, aml_phys_avg, aml_phys_err = bootstrap.average_and_std_arrays(aml_phys_dist)
    mpi_cen, mpi_val, mpi_err = bootstrap.average_and_std_arrays(mpi_dist)
    #aml_240_val, aml_240_avg, aml_240_err = bootstrap.average_and_std_arrays(aml_240_dist)

    print('M_pi = {} MeV <== am_l ='.format(siunitx(134.8, 0.3)), siunitx(aml_phys_val, aml_phys_err))
    #print('M_pi = 240 MeV <== am_l =', siunitx(aml_240_val, aml_240_err))

    fig = pl.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.fill_between(fit_x, fit_y_val - fit_y_err, fit_y_val + fit_y_err, color='0.8')
    ax.plot(fit_x, fit_y_val, color='black', label='GMOR Fit')
    ax.errorbar(aml, mpi_val, yerr=mpi_err, color='blue', marker='+', linestyle='none', label='Data')
    ax.errorbar([aml_phys_val], [135], xerr=[aml_phys_err], marker='+', color='red', label='Extrapolation')
    #ax.errorbar([aml_240_val], [240], xerr=[aml_240_err], marker='+', color='red')
    ax.set_title('Extrapolation to the Physical Point')
    ax.set_xlabel(r'$a m_\mathrm{ud}$')
    ax.set_ylabel(r'$M_\pi / \mathrm{MeV}$')
    util.dandify_axes(ax)

    ax = fig.add_subplot(2, 1, 2)
    ax.hist(aml_phys_dist - aml_phys_val, bins=50)
    ax.locator_params(nbins=6)
    ax.set_title('Bootstrap Bias')
    ax.set_xlabel(r'$(a m_\mathrm{ud}^\mathrm{phys})^* - a m_\mathrm{ud}^\mathrm{phys}$')
    util.dandify_axes(ax)

    util.dandify_figure(fig)
    fig.savefig('physical_point/GMOR.pdf')

    np.savetxt('physical_point/ampi-sq-vs-aml.tsv',
               np.column_stack([aml, ampi_sq_val, ampi_sq_err]))
    np.savetxt('physical_point/mpi-sq-vs-aml.tsv',
               np.column_stack([aml, mpi_sq_val, mpi_sq_err]))


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
