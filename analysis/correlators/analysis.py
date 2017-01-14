# Copyright © 2014-2015, 2017 Martin Ueding <dev@martin-ueding.de>

"""
Fragments for the analysis.
"""

import logging
import sys

import matplotlib.pyplot as pl
import numpy as np
import pandas as pd
import progressbar
import scipy.optimize as op
import scipy.stats

import correlators.fit


LOGGER = logging.getLogger(__name__)


def io_extract_mass(paths_in, path_out):
    two_points = correlators.loader.folded_list_loader(paths_in)

    sample_count = 3 * len(two_points)

    boot_correlators = correlators.bootstrap.generate_reduced_samples(
        orig_correlators, sample_count,
    )

    # Compute the correlation matrices from the bootstrap samples only.
    corr_matrix_2 = correlators.corrfit.correlation_matrix(correlators_2_val)

    omit_pre = 13

    inv_corr_mat_2 = corr_matrix_2[omit_pre:, omit_pre:].getI()
    inv_corr_mat_4 = corr_matrix_4[omit_pre:, omit_pre:].getI()

    # Generate a single time, they are all the same.
    time = np.array(range(len(correlators_2_val[0])))

    mean_result = analyze_2_4(
        time, mean_2_val, mean_2_err, inv_corr_mat_2,
        correlators.fit.cosh_fit_decorator, [0.222, mean_2_val[0]],
        mean_4_val, mean_4_err, inv_corr_mat_4,
        correlators.fit.cosh_fit_offset_decorator, [0.222, mean_4_val[0], 0],
        T, L, omit_pre, options,
    )

    boot_results = pd.DataFrame()

    p_bar = progressbar.ProgressBar()
    for sample_id in p_bar(range(sample_count)):
        boot_result = analyze_2_4(
            time, correlators_2_val[sample_id], correlators_2_err[sample_id],
            inv_corr_mat_2, correlators.fit.cosh_fit_decorator,
            [0.222, correlators_2_val[sample_id][0]],
            correlators_4_val[sample_id], correlators_4_err[sample_id],
            inv_corr_mat_4, correlators.fit.cosh_fit_offset_decorator,
            [0.222, correlators_4_val[sample_id][0], 0], T, L, omit_pre,
            options,
        )

        boot_series = pd.Series(boot_result)
        boot_results[sample_id] = boot_series

    boot_std = {
        key: np.std(np.array(dist))
        for key, dist in boot_results.T.iteritems()
    }

    boot_mean = {
        key: np.mean(np.array(dist))
        for key, dist in boot_results.T.iteritems()
    }

    for field in ['a_0', 'm_2', 'm_4', 'a_0*m_2']:
        pl.clf()
        pl.hist(boot_results.T[field])
        pl.title('Bootstrap distribution of {} in {}'.format(field, parameters['ensemble']))
        pl.savefig('{}_boot-hist_{}.pdf'.format(name, field))

    series = pd.Series({
        'a_0:1val': mean_result['a_0'],
        'a_0:2mean': boot_mean['a_0'],
        'a_0:3err': boot_std['a_0'],
        'm_2:1val': mean_result['m_2'],
        'm_2:2mean': boot_mean['m_2'],
        'm_2:3err': boot_std['m_2'],
        'm_4:1val': mean_result['m_4'],
        'm_4:2mean': boot_mean['m_4'],
        'm_4:3err': boot_std['m_4'],
        'a_0*m_2:1val': mean_result['a_0*m_2'],
        'a_0*m_2:2mean': boot_mean['a_0*m_2'],
        'a_0*m_2:3err': boot_std['a_0*m_2'],
        'p_value_2_val': mean_result['p_value_2'],
        'p_value_2_err': boot_std['p_value_2'],
        'p_value_4_val': mean_result['p_value_4'],
        'p_value_4_err': boot_std['p_value_4'],
        'm_pi/f_pi_val': m_pi_f_pi_val,
        'm_pi/f_pi_err': m_pi_f_pi_err,
        'L': parameters['L'],
        'T': parameters['T'],
        'a0*m_pi_paper_val': a0_mpi_paper_val,
        'a0*m_pi_paper_err': a0_mpi_paper_err,
    }, name=parameters['ensemble'])

    return series


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


def perform_fits(time, corr_val, corr_err, inv_corr_mat, fit_factory, p0, T,
                 omit_pre, options):
    # Generate a fit function from the factory.
    fit_function = fit_factory(T)

    # Select the data for the fit.
    used_x, used_y, used_yerr = correlators.fit._cut(time, corr_val.T,
                                                     corr_err.T, omit_pre, 0)
    used_y = used_y.T
    used_yerr = used_yerr.T

    # Perform a regular fit with the given initial parameters.
    fit_param, pconv = op.curve_fit(fit_function, used_x, used_y, p0=p0,
                                    sigma=used_yerr)

    if options.corr_fit:
        # Then perform a correlated fit using the previous result as the input.
        # This way it should be more stable.
        fit_param_corr, chi_sq = correlators.corrfit.curve_fit_correlated(
            fit_function, used_x, used_y, inv_corr_mat, p0=fit_param,
        )

        dof = len(used_x) - 1 - len(fit_param_corr)
        p_value = 1 - scipy.stats.chi2.cdf(chi_sq, dof)

        return fit_param_corr[0], p_value
    else:
        return fit_param[0], 0
