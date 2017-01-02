#!/bin/bash
# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

# Installs US QCD Chroma on my machines which both support the AVX ISA. The
# laptop is an Intel i5-2540M and the desktop is an AMD FX-8320.

set -e
set -u
set -x

export LC_ALL=C

basedir="$(pwd)"

source "$basedir/setup.sh"
source "$basedir/../common.sh"

source "$basedir/qdpxx.sh"
source "$basedir/qphix.sh"
source "$basedir/chroma.sh"
