#,!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <mu@martin-ueding.de>

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
    return 2 * aB * (aml - aml_cr)


def linear(x, a, b):
    return a * x + b


def main():
    options = _parse_args()
    R = 300

    # Read in the data from the paper.
    a_inv_val = 1616
    a_inv_err = 20
    a_inv_dist = bootstrap.make_dist(a_inv_val, a_inv_err, n=R)
    aml, ams, l, t, trajectories, ampi_val, ampi_err, amk_val, amk_err, f_k_f_pi_val, f_k_f_pi_err = util.load_columns('physical_point/gmor.txt')
    ampi_dist = bootstrap.make_dist(ampi_val, ampi_err, n=R)
    amk_dist = bootstrap.make_dist(amk_val, amk_err, n=R)
    mpi_dist = [ampi * a_inv for ampi, a_inv in zip(ampi_dist, a_inv_dist)]
    mk_dist = [amk * a_inv for amk, a_inv in zip(amk_dist, a_inv_dist)]

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

    ams_paper = -0.057
    ams_phys = ams_paper - amcr_val
    ams_red = 0.9 * ams_phys
    ams_bare_red = ams_red + amcr_val

    print(ams_paper, ams_phys, ams_red, ams_bare_red)

    print()
    print('Mass preconditioning masses:')

    amlq = aml - amcr_val
    for i in range(3):
        amprec = amlq * 10**i + amcr_val
        kappa = 1 / (amprec * 2 + 8)
        print('a m_prec:', amprec)
        print('κ', kappa)

    exit()

    diff_dist = [np.sqrt(2) * np.sqrt(mk**2 - 0.5 * mpi**2)
                 for mpi, mk in zip(mpi_dist, mk_dist)]
    diff_val, diff_avg, diff_err = bootstrap.average_and_std_arrays(diff_dist)

    popt_dist = [op.curve_fit(linear, mpi, diff)[0]
                 for mpi, diff in zip(mpi_dist, diff_dist)]
    fit_x = np.linspace(np.min(mpi_dist), np.max(mpi_dist), 100)
    fit_y_dist = [linear(fit_x, *popt)
                  for popt in popt_dist]
    fit_y_val, fit_y_avg, fit_y_err = bootstrap.average_and_std_arrays(fit_y_dist)

    # Physical meson masses from FLAG paper.
    mpi_phys_dist = bootstrap.make_dist(134.8, 0.3, R)
    mk_phys_dist = bootstrap.make_dist(494.2, 0.3, R)
    mpi_phys_val, mpi_phys_avg, mpi_phys_err = bootstrap.average_and_std_arrays(mpi_phys_dist)
    ampi_phys_dist = [mpi_phys / a_inv
                      for a_inv, mpi_phys in zip(a_inv_dist, mpi_phys_dist)]
    amk_phys_dist = [mk_phys / a_inv
                     for a_inv, mk_phys in zip(a_inv_dist, mk_phys_dist)]
    ampi_phys_val, ampi_phys_avg, ampi_phys_err = bootstrap.average_and_std_arrays(ampi_phys_dist)
    amk_phys_val, amk_phys_avg, amk_phys_err = bootstrap.average_and_std_arrays(amk_phys_dist)
    print('aM_pi phys =', siunitx(ampi_phys_val, ampi_phys_err))
    print('aM_k phys =', siunitx(amk_phys_val, amk_phys_err))

    new_b_dist = [np.sqrt(mk_phys**2 - 0.5 * mpi_phys**2) - popt[0] * mpi_phys
                  for mpi_phys, mk_phys, popt in zip(mpi_phys_dist, mk_phys_dist, popt_dist)]

    diff_sqrt_phys_dist = [np.sqrt(mk_phys**2 - 0.5 * mpi_phys**2)
                           for mpi_phys, mk_phys in zip(mpi_phys_dist, mk_phys_dist)]
    diff_sqrt_phys_val, diff_sqrt_phys_avg, diff_sqrt_phys_err = bootstrap.average_and_std_arrays(diff_sqrt_phys_dist)

    ex_x = np.linspace(120, 700, 100)
    ex_y_dist = [linear(ex_x, popt[0], b)
                 for popt, b in zip(popt_dist, new_b_dist)]
    ex_y_val, ex_y_avg, ex_y_err = bootstrap.average_and_std_arrays(ex_y_dist)

    ams_art_dist = [
        linear(mpi, popt[0], b)**2 / a_inv**2 / aB - amcr
        for mpi, popt, b, a_inv, aB, amcr in zip(mpi_dist, popt_dist, new_b_dist, a_inv_dist, aB_dist, amcr_dist)]
    ams_art_val, ams_art_avg, ams_art_err = bootstrap.average_and_std_arrays(ams_art_dist)
    print('a m_s with artifacts', siunitx(ams_art_val, ams_art_err))

    fig, ax = util.make_figure()
    ax.fill_between(fit_x, fit_y_val + fit_y_err, fit_y_val - fit_y_err, color='red', alpha=0.2)
    ax.plot(fit_x, fit_y_val, label='Fit', color='red')
    ax.fill_between(ex_x, ex_y_val + ex_y_err, ex_y_val - ex_y_err, color='orange', alpha=0.2)
    ax.plot(ex_x, ex_y_val, label='Extrapolation', color='orange')
    ax.errorbar(mpi_val, diff_val, xerr=mpi_err, yerr=diff_err, linestyle='none', label='Data (Dürr 2010)')
    ax.errorbar([mpi_phys_val], [diff_sqrt_phys_val], xerr=[mpi_phys_err], yerr=[diff_sqrt_phys_err], label='Physical Point (Aoki)')
    util.save_figure(fig, 'test')

    np.savetxt('artifact-bmw-data.tsv',
               np.column_stack([mpi_val, diff_val, mpi_err, diff_err]))
    np.savetxt('artifact-bmw-fit.tsv',
               np.column_stack([fit_x, fit_y_val]))
    np.savetxt('artifact-bmw-band.tsv',
               bootstrap.pgfplots_error_band(fit_x, fit_y_val, fit_y_err))
    np.savetxt('artifact-phys-data.tsv',
               np.column_stack([[mpi_phys_val], [diff_sqrt_phys_val], [mpi_phys_err], [diff_sqrt_phys_err]]))
    np.savetxt('artifact-phys-fit.tsv',
               np.column_stack([ex_x, ex_y_val]))
    np.savetxt('artifact-phys-band.tsv',
               bootstrap.pgfplots_error_band(ex_x, ex_y_val, ex_y_err))
    np.savetxt('artifact-ms.tsv',
               np.column_stack([mpi_val, ams_art_val, mpi_err, ams_art_err]))

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
