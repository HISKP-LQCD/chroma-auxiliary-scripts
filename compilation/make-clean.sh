#!/bin/bash
# Copyright © 2016 Martin Ueding <martin-ueding.de>

set -e
set -u
set -x

cd $HOME

rm -rf local

for dir in chroma gmp-6.1.1 libxml2 qdpxx qmp
do
    pushd $dir
    make clean || true
    rm -f Makefile build-succeeded
    popd
done
