#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

set -e
set -u

mkdir $1
pushd $1
cp $HOME/Sources/chroma-test-run/{jureca-job-script.sh,testrun.ini.xml} .
cp $HOME/local-jureca/bin/hmc .
popd
