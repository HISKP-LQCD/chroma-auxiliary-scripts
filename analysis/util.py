#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import numpy as np


def load_columns(filename):
    data = np.loadtxt(filename)
    data2d = np.atleast_2d(data)
    shape = data2d.shape
    num_cols = shape[1]

    cols = [data2d[:, i] for i in range(num_cols)]
    return cols
