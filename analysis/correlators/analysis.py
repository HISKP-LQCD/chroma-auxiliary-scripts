# Copyright © 2014-2015, 2017 Martin Ueding <dev@martin-ueding.de>

"""
Fragments for the analysis.
"""

import logging
import sys

import matplotlib.pyplot as pl
import numpy as np
import scipy.optimize as op
import scipy.stats

import bootstrap
import correlators.corrfit
import correlators.fit
import correlators.loader
import correlators.transform
import util


LOGGER = logging.getLogger(__name__)


def io_effective_mass(paths_in, path_out):
    twopts_orig = correlators.loader.folded_list_loader(paths_in)
    sample_count = 3 * len(twopts_orig)
    b_twopts = bootstrap.Boot(bootstrap.make_dist_draw(twopts_orig, sample_count))
    b_effective = bootstrap.Boot([
        correlators.transform.effective_mass_cosh(bootstrap.average_arrays(twopts))
        for twopts in b_twopts.dist
    ])
    t = np.arange(1, len(twopts_orig[0]) - 1, dtype=float)
    print(t)
    print(b_effective.cen)
    print(b_effective.err)
    np.savetxt(path_out,
               np.column_stack([t, b_effective.cen, b_effective.err]))



def io_extract_mass(paths_in, path_out):
    twopts_orig = correlators.loader.folded_list_loader(paths_in)

    sample_count = 3 * len(twopts_orig)

    b_twopts = bootstrap.Boot(bootstrap.make_dist_draw(twopts_orig, sample_count))

    b_corr_matrix = bootstrap.Boot([
        correlators.corrfit.correlation_matrix(twopts)
        for twopts in b_twopts.dist])

    omit_pre = 7

    b_inv_corr_mat = bootstrap.Boot([
        corr_matrix[omit_pre:, omit_pre:].getI()
        for corr_matrix in b_corr_matrix.dist])

    time_extent = len(b_twopts.dist[0][0])
    time = np.arange(time_extent)

    fit_function = correlators.fit.cosh_fit_decorator(2 * (time_extent - 1))
    b_fit_param = bootstrap.Boot([
        perform_fits(time,
                     bootstrap.average_arrays(twopts),
                     bootstrap.std_arrays(twopts),
                     inv_corr_mat,
                     fit_function,
                     (0.4, 1.0, 0.0),
                     omit_pre)
        for twopts, inv_corr_mat in zip(b_twopts.dist, b_inv_corr_mat.dist)])

    fig, ax = util.make_figure()
    ax.errorbar(time, bootstrap.average_arrays(b_twopts.cen), bootstrap.std_arrays(b_twopts.cen))
    ax.plot(time, fit_function(time, *b_fit_param.cen))
    ax.set_yscale('log')
    util.save_figure(fig, 'test-corr.pdf')

    print('cen', b_fit_param.cen[0])
    print('val', b_fit_param.val[0])
    print('err', b_fit_param.err[0])

    print('len', len(twopts_orig), len(b_fit_param.dist))

    np.savetxt(path_out,
               np.column_stack([b_fit_param.cen[0], b_fit_param.val[0], b_fit_param.err[0]]))


def unwrap_correlator_values(boot_correlators, index):
    return [
        bootstrap_set[index][0]
        for bootstrap_set in boot_correlators
    ]


def unwrap_correlator_errors(boot_correlators, index):
    return [
        bootstrap_set[index][1]
        for bootstrap_set in boot_correlators
    ]


def perform_fits(time, corr_val, corr_err, inv_corr_mat, fit_function, p0,
                 omit_pre, regular_first=False):
    # Select the data for the fit.
    used_x, used_y, used_yerr = correlators.fit._cut(time, corr_val.T,
                                                     corr_err.T, omit_pre, 0)
    used_y = used_y.T
    used_yerr = used_yerr.T

    if regular_first:
        # Perform a regular fit with the given initial parameters.
        fit_param, pconv = op.curve_fit(fit_function, used_x, used_y, p0=p0,
                                        sigma=used_yerr)
    else:
        fit_param = p0

    # Then perform a correlated fit using the previous result as the input.
    # This way it should be more stable.
    fit_param_corr, chi_sq = correlators.corrfit.curve_fit_correlated(
        fit_function, used_x, used_y, inv_corr_mat, p0=fit_param,
    )


    dof = len(used_x) - 1 - len(fit_param_corr)
    p_value = 1 - scipy.stats.chi2.cdf(chi_sq, dof)


    return fit_param_corr
