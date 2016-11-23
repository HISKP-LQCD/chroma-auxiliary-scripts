#!/bin/bash
# Copyright © 2016 Martin Ueding <dev@martin-ueding.de>

set -e
set -u
set -x

exit 1

clone-if-needed() {
local url="$1"
local dir="$2"
local branch="$3"

if ! [[ -d "$dir" ]]
then
    git clone "$url" --recursive -b "$branch"
fi
}

configure-make() {
local dir="$1"
local extra_configure_flags="${2-}"

pushd "$dir"
if ! [[ -f .build-succeeded ]]
then
    if ! [[ -f configure ]]
    then
        ./autogen.sh
    fi
    if ! [[ -f Makefile ]]
    then
        ./configure "${configure_flags[@]}" $extra_configure_flags
    fi
    nice make -j $(nproc) CFLAGS="\"${cflags[@]}\"" CXXFLAGS="\"${cxxflags[@]}\""
    touch .build-succeeded
fi
popd
}

#--with-libxml2=/usr/include/libxml2/libxml

cxxflags=( -O2 -msse -finline-limit=50000 -march=native --std=c++11 -fopenmp )
cflags=( -O2 -msse -finline-limit=50000 -march=native --std=c99 -fopenmp )
configure_flags=( --enable-sse --enable-sse2 --enable-openmp \
    --enable-parallel-arch=scalar  CXX=/usr/bin/g++ CC=/usr/bin/gcc \
    CFLAGS="${cflags[@]}" CXXFLAGS="${cxxflags[@]}" )

clone-if-needed https://github.com/martin-ueding/qdpxx.git qdpxx martins-fedora24-build
clone-if-needed https://github.com/martin-ueding/chroma.git chroma submodules-via-https

configure-make qdpxx
configure-make chroma "--with-gmp=/usr/include/ --with-qdp=../qdpxx"

echo "This took $SECONDS seconds."
