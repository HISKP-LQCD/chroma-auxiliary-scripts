# Copyright © 2017 Martin Ueding <martin-ueding.de>

import glob
import os

from lxml import etree
import numpy as np
import scipy.optimize as op

import util


def io_extract_pion_corr(path_in, path_out):
    try:
        tree = etree.parse(path_in)
    except etree.XMLSyntaxError as e:
        print('XML file could not be loaded')
        print(e)
        
        np.savetxt(path_out, [])

    update_no = int(tree.xpath('//StartUpdateNum/text()')[0])
    gamma_blocks = tree.xpath('//Point_Point_Wilson_Mesons/elem')

    for gamma_block in gamma_blocks:
        gamma_value = int(gamma_block.xpath('gamma_value/text()')[0])
        print(gamma_value)
        if gamma_value != 15:
            continue

        for momentum in gamma_block.xpath('momenta/elem'):
            sink_mom = momentum.xpath('sink_mom/text()')[0]
            if sink_mom != '0 0 0':
                continue

            re = momentum.xpath('mesprop/elem/re/text()')
            im = momentum.xpath('mesprop/elem/im/text()')

            re = np.array(list(map(float, re)))
            im = np.array(list(map(float, im)))
            t = np.arange(len(re))

            np.savetxt(path_out, np.column_stack([t, re, im]))
            return
