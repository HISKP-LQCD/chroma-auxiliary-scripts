# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import glob
import os

from lxml import etree
import numpy as np
import scipy.optimize as op

import util


def main(options):
    for dirname in options.dirname:
        process_directory(dirname)


def eff_mass(t, m, a, L):
    r = a * (np.exp(- m * t) + np.exp(- m * (L - t)))
    return r


def process_directory(dirname):
    for xml_file in sorted(glob.glob(os.path.join(dirname, '*.corr.xml'))):
        try:
            tree = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            print('XML file could not be loaded')
            print(e)
            continue

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

                np.savetxt(os.path.join(dirname, 'extract-pi_corr-{}.tsv'.format(update_no)),
                           np.column_stack([t, re, im]))

                sel = (5 <= t) & (t <= 31 - 5)

                fit_func = lambda t, m, a: eff_mass(t, m, a, 32)
                popt, pconv = op.curve_fit(fit_func, t[sel], re[sel], sigma=re[sel])
                print(popt)
                x = np.linspace(np.min(t), np.max(t), 100)
                y = fit_func(x, *popt)

                np.savetxt(os.path.join(dirname, 'extract-pi_corr_fit-{}.tsv'.format(update_no)),
                           np.column_stack([x, y]))
