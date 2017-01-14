# Copyright © 2014-2015, 2017 Martin Ueding <dev@martin-ueding.de>

'''
Helper functions to load the binary data that I was given from
``/hiskp2/correlators/``.
'''

from __future__ import division, absolute_import, print_function, \
    unicode_literals

import os
import os.path
import re
import logging

import numpy as np


TWO_PATTERN = re.compile(r'C2_pi\+-_conf(\d{4}).dat')
FOUR_PATTERN = re.compile(r'C4_(\d)_conf(\d{4}).dat')

CONFIGURATION_PATTERN = re.compile(r'''
                                   ^.*
                                   (?P<path>
                                   (?P<ensemble>[ABCD][0-9.]+)_
                                   L(?P<L>\d+)_
                                   T(?P<T>\d+)_
                                   beta(?P<beta>\d+)_
                                   mul(?P<mul>\d+)_
                                   musig(?P<musig>\d+)_
                                   mudel(?P<mudel>\d+)_
                                   kappa(?P<kappa>\d+)
                                   .*)$
                                   ''', re.X)

LOGGER = logging.getLogger(__name__)


def folder_loader(path):
    '''
    Loads all the two-point and four-point correlation functions from the given
    folder.
    '''
    two_points = []
    four_points = {
        1: [],
        2: [],
        3: [],
    }

    path_m = CONFIGURATION_PATTERN.match(path)
    if path_m:
        parameters = path_m.groupdict()
    else:
        raise RuntimeError(
            'Cannot parse parameters out of "{}". Please check the regular '
            'expression in `loader.py` and/or give a complete path that '
            'includes all the parameters.'.format(path)
        )


    for filename in sorted(os.listdir(path)):
        # Load and fold the data.
        data = fold_data(correlator_loader(os.path.join(path, filename)))

        m = TWO_PATTERN.match(filename)
        if m:
            two_points.append(data)
            continue

        m = FOUR_PATTERN.match(filename)
        if m:
            number = int(m.group(1))
            if number in four_points:
                four_points[number].append(data)
            else:
                LOGGER.warning('Number %s is unexpected in `%s`.', number,
                               filename)
            continue

        raise RuntimeError('`{}` has unforseen format.'.format(filename))

    four_point = [
        c1 + c2 - 2 * c3
        for c1, c2, c3 in zip(four_points[1], four_points[2], four_points[3])
    ]

    return two_points, four_point, parameters


def correlator_loader(filename):
    '''
    Loads binary correlator files.
    
    Such a file would be
    ``/hiskp2/correlators/A100.24_L24_T48_beta190_mul0100_musig150_mudel190_kappa1632550/ev120/TB2_SO_LI6_new/C2_pi+-_conf0501.dat``.

    It is assumed that the data in the files are only *little endian 8-byte
    float* numbers, real and imaginary part right after each other.

    :param str filename: Path to the binary file
    :returns: NumPy array with complex numbers
    :rtype: np.array
    '''
    dtype = np.dtype(np.complex128)
    data = np.real(np.fromfile(filename, dtype))

    return data


def loader_iterator(filenames):
    '''
    Iterator that gives the data to the given filenames.

    :param list filenames: List of filenames (str)
    '''
    for filename in filenames:
        data = correlator_loader(filename)
        yield data


def folded_list_loader(filenames):
    return [fold_data(data) for data in loader_iterator(filenames)]


def fold_data(val):
    r'''
    Folds the data around the middle element and averages.

    The expectation is to yield a :math:`\cosh` function. The transformation of
    the :math:`\{x_i\colon i = 1, \ldots, N\}` will generate new data points
    like this:

    .. math::

        y_i := \frac{x_i + x_{N-i}}2

    :param np.array val: Array with an even number of elements, values
    :param np.array err: Array with an even number of elements, errors
    :returns: Folded array with :math:`N/2` elements
    :rtype: np.array
    '''
    n = len(val)
    second_rev_val = val[n//2+1:][::-1]
    first_val = val[:n//2+1]
    first_val[1:-1] += second_rev_val
    first_val[1:-1] /= 2.

    return first_val
