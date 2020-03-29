# Copyright © 2014-2015, 2017-2018 Martin Ueding <mu@martin-ueding.de>

"""
Plots of data sets.
"""

import logging

import matplotlib.figure
import numpy as np

import correlators.bootstrap
import correlators.fit
import correlators.transform


LOGGER = logging.getLogger(__name__)


def plot_correlator(sets, name, shift, offset=False):
    folded_val, folded_err = correlators.bootstrap.bootstrap_pre_transform(
        correlators.bootstrap.average_arrays, sets
    )

    time_folded = np.array(range(len(folded_val)))

    fig_f = matplotlib.figure.Figure()
    ax2 = fig_f.add_subplot(1, 1, 1)

    ax2.errorbar(time_folded, folded_val, yerr=folded_err, linestyle='none',
                 marker='+', label='folded')

    fit_param = {'color': 'gray'}
    used_param = {'color': 'blue'}
    data_param = {'color': 'black'}

    if offset:
        fit_func = correlators.fit.cosh_fit_offset_decorator(shift)
        p0 = [0.45, folded_val[0], 0]
    else:
        fit_func = correlators.fit.cosh_fit_decorator(shift)
        p0 = [0.22, folded_val[0]]

    try:
        p = correlators.fit.fit_and_plot(ax2, fit_func, time_folded, folded_val,
                                         folded_err, omit_pre=13, p0=p0,
                                         fit_param=fit_param, used_param=used_param,
                                         data_param=data_param)
        print('Fit parameters folded (mass, amplitude, offset:', p)
    except ValueError as e:
        LOGGER.error('ValueError: %s', str(e))

    ax2.set_yscale('log')
    ax2.margins(0.05, tight=False)
    ax2.set_title('Folded Correlator')
    ax2.set_xlabel(r'$t/a$')
    ax2.set_ylabel(r'$\frac{1}{2} [C(t) + C(T-t)]$')
    ax2.grid(True)

    canvas.print_figure('{}_folded.pdf'.format(name))


def plot_effective_mass(sets, name):
    m_eff_val1, m_eff_err1 = correlators.bootstrap.bootstrap_pre_transform(
        correlators.transform.effective_mass_cosh, sets
    )
    time = np.arange(len(m_eff_val1)+2)
    time_cut = time[1:-1]

    fig = matplotlib.figure.Figure()
    ax = fig.add_subplot(2, 1, 1)
    ax2 = fig.add_subplot(2, 1, 2)

    ax.errorbar(time_cut, m_eff_val1, yerr=m_eff_err1, linestyle='none',
                marker='+')
    ax.set_title(r'Effective Mass $\cosh^{-1} ([C(t-1)+C(t+1)]/[2C(t)])$')
    ax.set_xlabel(r'$t/a$')
    ax.set_ylabel(r'$m_\mathrm{eff}(t)$')
    ax.grid(True)
    ax.margins(0.05, 0.05)

    ax2.errorbar(time_cut[8:], m_eff_val1[8:], yerr=m_eff_err1[8:],
                 linestyle='none', marker='+')
    # ax2.errorbar([max(time_cut[8:])], [0.22293], [0.00035], marker='+')
    ax2.set_xlabel(r'$t/a$')
    ax2.set_ylabel(r'$m_\mathrm{eff}(t)$')
    ax2.grid(True)
    ax2.margins(0.05, 0.05)

    canvas.print_figure('{}_m_eff.pdf'.format(name))
