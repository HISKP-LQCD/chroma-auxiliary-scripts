#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

# Installs US QCD Chroma on JURECA, an Intel Xeon E5-2680 v3 Haswell + NVIDIA
# K40 supercomputer.

set -e
set -u
set -x

basedir="$(pwd)"
sourcedir="$HOME/Sources-JURECA"

mkdir -p "$sourcedir"
cd "$sourcedir"

source "$basedir/setup.sh"

source "$basedir/qmp.sh"
source "$basedir/libxml2.sh"
source "$basedir/qdpxx.sh"
