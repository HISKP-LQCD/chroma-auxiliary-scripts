# Copyright © 2014-2015, 2017 Martin Ueding <martin-ueding.de>

import numpy as np
import scipy.optimize as op
import scipy.stats


def _cut(x, y, yerr, omit_pre, omit_post):
    if omit_post == 0:
        used_x = x[omit_pre:]
        used_y = y[omit_pre:]
        if yerr is None:
            used_yerr = None
        else:
            used_yerr = yerr[omit_pre:]
    else:
        end = - omit_post - 1
        used_x = x[omit_pre:end]
        used_y = y[omit_pre:end]
        if yerr is None:
            used_yerr = None
        else:
            used_yerr = yerr[omit_pre:end]

    return used_x, used_y, used_yerr


def fit(func, x, y, yerr=None, omit_pre=0, omit_post=0, p0=None):
    used_x, used_y, used_yerr = _cut(x, y, yerr, omit_pre, omit_post)
    popt, pconv = op.curve_fit(func, used_x, used_y, p0=p0, sigma=used_yerr)

    return popt


def fit_and_plot(axes, func, x, y, yerr=None, omit_pre=0, omit_post=0, p0=None,
                 fit_param={}, data_param={}, used_param={}, axes_res=None):
    used_x, used_y, used_yerr = _cut(x, y, yerr, omit_pre, omit_post)
    popt = fit(func, used_x, used_y, used_yerr, p0=p0)

    fx = np.linspace(np.min(x), np.max(x), 1000)
    fy = func(fx, *popt)

    param = {}
    param = dict(param.items() + fit_param.items())
    axes.plot(fx, fy, **param)

    param = {'marker': '+', 'linestyle': 'none'}
    param = dict(param.items() + data_param.items())
    axes.errorbar(x, y, yerr=yerr, **param)

    param = {'marker': '+', 'linestyle': 'none'}
    param = dict(param.items() + used_param.items())
    axes.errorbar(used_x, used_y, yerr=used_yerr, **param)

    axes_res = axes.twinx()
    axes_res.errorbar(used_x, used_y - func(used_x, *popt), yerr=used_yerr,
                      marker='+', linestyle='none', color='red', alpha=0.3)
    axes_res.set_ylabel('Residual')

    axes_res.plot([np.min(used_x), np.max(used_x)], [0, 0], color='red',
                  alpha=0.2)

    dof = len(used_y) - len(popt) - 1
    chisq, p = scipy.stats.chisquare(used_y, func(used_x, *popt),
                                     ddof=len(popt))

    print('χ2:', chisq)
    print('χ2/DOF:', chisq/dof)
    print('p:', p)

    return popt


def cosh_fit_decorator(shift):
    def cosh_fit(x, m, a, offset):
        '''

        .. math::

            \operatorname{fit}(x; m_1, m_2, a_1, a_2)
            = a_1 \exp(- m_1 x) + a_2 \exp(- m_2 [n - x])

        :param np.array x: Input values
        :param float m: Effective mass
        :param float a: Amplitude exponential
        :param int shift: Value of :math:`x` where :math:`f(x) = f(0)`
        '''
        y = shift - x
        first = a * np.exp(-x*m)
        second = a * np.exp(-y*m)
        return first + second + offset

    return cosh_fit


def cosh_fit_offset_decorator(shift):
    cosh_fit = cosh_fit_decorator(shift)

    def cosh_fit_offset(x, m, a, offset):
        '''

        .. math::

            \operatorname{fit}(x; m_1, m_2, a_1, a_2, \mathrm{offset})
            = a_1 \exp(- m_1 x) + a_2 \exp(- m_2 [n - x]) + \mathrm{offset}

        :param np.array x: Input values
        :param float m: Effective mass
        :param float a: Amplitude exponential
        :param int shift: Value of :math:`x` where :math:`f(x) = f(0)`
        :param float offset: Constant offset
        '''
        return cosh_fit(x, m, a) + offset

    return cosh_fit_offset


def exp_fit(x, m1, a1, offset):
    '''
    :param np.array x: Input values
    :param float m1: Effective mass for falling exponential
    :param float a1: Amplitude for falling exponential
    :param float offset: Constant offset
    '''
    return a1 * np.exp(-x*m1) + offset
