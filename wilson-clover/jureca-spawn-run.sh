#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

set -e
set -u

mkdir $1
pushd $1
cp $HOME/Sources/chroma-auxiliary-scripts/wilson-clover/{jureca-job-script.sh,hmc-wilson-clover.ini.xml} .
cp $HOME/jureca-local-icc/bin/hmc .
popd