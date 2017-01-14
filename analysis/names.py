# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

import re
import os


def _make_dir(filename):
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)


def _ensure_dir(function):
    def f(path_in):
        path_out = function(path_in)
        _make_dir(path_out)
        return path_out
    return f


@_ensure_dir
def correlator_tsv(xml_file):
    config = re.search('config-(\d+)', xml_file).group(0)
    dirname = os.path.dirname(xml_file)
    corr_tsv = os.path.join(dirname, 'extract', 'corr', 'corr.config-{}.tsv'.format(config))
    return corr_tsv
