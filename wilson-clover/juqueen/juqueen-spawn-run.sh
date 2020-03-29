#!/bin/bash
# Copyright © 2016 Martin Ueding <mu@martin-ueding.de>

set -e
set -u

mkdir $1
pushd $1
cp $HOME/chroma-test-run/{juqueen-job-script.sh,testrun.ini.xml} .
cp $HOME/local-juqueen/bin/hmc .
popd
