#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

# Installs US QCD Chroma on JUQUEEN, an IBM Blue Gene/Q supercomputer.
#
# Chroma needs C++11, this means that the IBM XL compiler is ruled out and at
# least version 4.8 of GCC is needed. 4.9 is better because that can actually
# do C++11 and not only C++0x.
#
# This leads to a problem because the system wide installation of the `gmp`
# library uses the old GCC 4.4 header files which are not compatible with GCC
# 4.9 any more. This means that `gmp` has to be build from source.
#
# For some reasons the `libxml2` system installation does not link properly, so
# that is installed from source as well. That however has some errors in the
# GNU Autotools build scripts, the `./configure` fails with syntax errors. So
# far I have just manually patched the `configure` script to remove this stuff.

set -e
set -u
set -x

basedir=$(pwd)

mkdir -p $HOME/Sources-juqueen
cd $HOME/Sources-juqueen

source $basedir/setup.sh

source $basedir/libxml2.sh
source $basedir/gmp.sh
source $basedir/qmp.sh
source $basedir/qdpxx.sh
source $basedir/chroma.sh

echo "This took $SECONDS seconds."
