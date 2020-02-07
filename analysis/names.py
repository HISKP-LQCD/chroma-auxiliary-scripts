# Copyright © 2017-2018 Martin Ueding <martin-ueding.de>

import re
import os


def _make_dir(filename):
    dirname = os.path.dirname(filename)
    os.makedirs(dirname, exist_ok=True)


def _ensure_dir(function):
    def f(*args, **kwargs):
        path_out = function(*args, **kwargs)
        _make_dir(path_out)
        return path_out
    return f


@_ensure_dir
def correlator_tsv(xml_file, meson):
    config = re.search('config-(\d+)', xml_file).group(0)
    dirname = os.path.dirname(xml_file)
    corr_tsv = os.path.join(dirname, 'extract', 'corr', 'corr.config-{}.{}.tsv'.format(config, meson))
    return corr_tsv


@_ensure_dir
def wflow_xml_shard_name(xml_file, key):
    dirname = os.path.dirname(xml_file)
    basename = os.path.basename(xml_file)
    name = os.path.join(dirname, 'shard', 'wflow', 'shard-{}.{}.tsv'.format(basename, key))
    return name


@_ensure_dir
def wflow_tsv(dirname, name):
    path_out = os.path.join(dirname, 'extract', 'extract-{}.tsv'.format(name))
    return path_out


@_ensure_dir
def log_shard(logfile):
    dirname = os.path.dirname(logfile)
    basename = os.path.basename(logfile)
    return os.path.join(dirname, 'shard', 'logfile', 'shard-' + basename + '.json')


@_ensure_dir
def log_extract(directory):
    return os.path.join(directory, 'extract', 'extract-log.json')


@_ensure_dir
def log_long(directory):
    return os.path.join(directory, 'extract', 'log-long.csv')


@_ensure_dir
def xpath_shard(xml_file, key):
    dirname = os.path.dirname(xml_file)
    basename = os.path.basename(xml_file)
    return os.path.join(dirname, 'shard', 'xmlfile', 'shard-{}-{}.tsv'.format(basename, key))


@_ensure_dir
def xmllog_extract(directory, key):
    return os.path.join(directory, 'extract', 'extract-{}.tsv'.format(key))


@_ensure_dir
def plot(dirname, name):
    return os.path.join(dirname, 'plot', 'plot-{}.pdf'.format(name))


@_ensure_dir
def pion_mass(dirname):
    return os.path.join(dirname, 'extract', 'extract-Mpi.pdf')


@_ensure_dir
def json_extract(dirname, name):
    return os.path.join(dirname, 'extract', 'extract-{}.json'.format(name))


@_ensure_dir
def tsv_extract(dirname, name):
    return os.path.join(dirname, 'extract', 'extract-{}.tsv'.format(name))
