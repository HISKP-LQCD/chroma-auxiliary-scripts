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

# Load the appropriate modules and output the present versions.

module load autotools

module list

# Clones a git repository if the directory does not exist. It does not call
# `git pull`.

clone-if-needed() {
    local url="$1"
    local dir="$2"
    local branch="$3"

    if ! [[ -d "$dir" ]]
    then
        git clone "$url" --recursive -b "$branch"
    fi
}

wget-if-needed() {
    local url="$1"
    local dir="$2"

    if ! [[ -d "$dir" ]]; then
        base=${url##*/}
        wget $url
        tar -xf $base
    fi
}

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.

make_smp_template="-j $(nproc)"
make_smp_flags="${SMP-$make_smp_template}"

make-make-install() {
    if ! [[ -f build-succeeded ]]; then
        nice make $make_smp_flags
        make install
        touch build-succeeded
        pushd $prefix/lib
        rm -f *.so *.so.*
        popd
    fi
}

# Basic flags that are used for every single project compiled.

prefix="$HOME/local"

compiler=${COMPILER-clang}

case $compiler in
    ibmxl)
        cc_name=mpixlc_r
        cxx_name=mpixlcxx_r
        color_flags=""
        openmp_flags="-qsmp=omp -qnosave"
        base_flags="-qarch=qp -O2"
        cxx11_flags="-qlanglvl=extended0x"
        ;;
    gcc)
        module load gcc/4.9.3
        cc_name=mpigcc
        cxx_name=mpig++
        color_flags="-fdiagnostics-color=auto"
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -Wall -Wpedantic $color_flags"
        cxx11_flags="--std=c++11"
        ;;
    clang)
        module load clang/3.7.r236977
        cc_name=mpicc
        cxx_name=mpic++
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -Wall -Wpedantic"
        cxx11_flags="--std=c++11"
        ;;
    *)
        echo "This compiler is not supported by this script. Choose another one."
        exit 1
        ;;
esac

cc=$(which $cc_name)
cxx=$(which $cxx_name)

cross_compile_flags="--host=powerpc64-bgq-linux --build=powerpc64-unknown-linux-gnu"
mpich_include_flags="-I/usr/local/bg_soft/mpich3/include"

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix $cross_compile_flags --disable-shared --enable-static CC=$cc CXX=$cxx"

###############################################################################
#                           gmp: GNU Multi Precision                          #
###############################################################################

if ! [[ -d gmp-6.1.1 ]]; then
    wget https://gmplib.org/download/gmp/gmp-6.1.1.tar.xz
    tar -xf gmp-6.1.1.tar.xz
fi

pushd gmp-6.1.1
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        CFLAGS="$cflags"
fi
make-make-install
popd

###############################################################################
#                                   libxml2                                   #
###############################################################################

clone-if-needed git://git.gnome.org/libxml2 libxml2 v2.9.4

pushd libxml2
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f Makefile ]]; then
    pushd m4
    ln -fs /usr/share/aclocal/pkg.m4 .
    popd
    NOCONFIGURE=yes ./autogen.sh
    ./configure $base_configure \
        --without-zlib \
        --without-python \
        --without-readline \
        --without-threads \
        --without-history \
        --without-reader \
        --without-writer \
        --with-output \
        --without-ftp \
        --without-http \
        --without-pattern \
        --without-catalog \
        --without-docbook \
        --without-iconv \
        --without-schemas \
        --without-schematron \
        --without-modules \
        --without-xptr \
        --without-xinclude \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                             bagel_wilson_dslash                             #
###############################################################################

wget-if-needed http://www2.ph.ed.ac.uk/~paboyle/bagel/bagel_wilson_dslash-1.4.6.tar.gz bagel_wilson_dslash-1.4.6

pushd bagel_wilson_dslash-1.4.6
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    CC=$cc CXX=$cxx ./configure $base_configure \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                      Bagel assembler kernel generator                       #
###############################################################################

wget-if-needed http://www2.ph.ed.ac.uk/~paboyle/bagel/bagel-3.3.tar bagel

pushd bagel
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                                     bfm                                     #
###############################################################################

#module load gsl
#
#clone-if-needed https://github.com/martin-ueding/bfm.git bfm master
#
#pushd bfm
#extra_common="-I$GSL_INCLUDE -I$HOME/local/include -I$HOME/local/include/libxml2 -fpermissive"
#cflags="$base_cflags $extra_common $openmp_flags"
#cxxflags="$base_cxxflags $extra_common $openmp_flags $cxx11_flags"
#if ! [[ -f configure ]]; then
#    automake --add-missing
#    autoreconf -f
#fi
#if ! [[ -f Makefile ]]; then
#    ./configure $base_configure \
#        --enable-itype=uint64_t --enable-isize=8 --enable-ifmt=%lx \
#        --enable-istype=uint32_t --enable-issize=4 --enable-isfmt=%x \
#        --enable-comms=QMP \
#        --enable-qdp \
#        --enable-spidslash=yes \
#        --with-libxml2="$prefix/bin/xml2-config" \
#        --enable-thread-model=spi \
#        --with-bagel=$prefix \
#        --with-qdp=$prefix \
#        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
#fi
#make-make-install
#popd

###############################################################################
#                   bagel_qdp: Bagel code generator for QDP                   #
###############################################################################

clone-if-needed https://github.com/usqcd-software/bagel_qdp.git bagel_qdp master

pushd bagel_qdp
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-target-cpu=bgl \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                         qmp: QCD Message Passaging                          #
###############################################################################

clone-if-needed https://github.com/usqcd-software/qmp.git qmp master

pushd qmp
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-bgspi \
        --enable-bgq \
        --with-qmp-comms-type=MPI \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#              qphix: QCD for Intel Xeon Phi and Xeon processors              #
###############################################################################

clone-if-needed https://github.com/JeffersonLab/qphix.git qphix master

pushd qphix
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --disable-mm-malloc \
        --disable-testing \
        --enable-clover \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --with-qdp++="$prefix" \
        --with-qdp="$prefix" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                        qdpxx: QCD Data Parallel C++                         #
###############################################################################

clone-if-needed https://github.com/martin-ueding/qdpxx.git qdpxx martins-fedora24-build

pushd qdpxx
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-bgq-thread-binding \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                                   Chroma                                    #
###############################################################################

clone-if-needed https://github.com/martin-ueding/chroma.git chroma submodules-via-https

pushd chroma
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
if ! [[ -f configure ]]; then ./autogen.sh; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-bgq-thread-binding \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --with-gmp="$prefix" \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qdp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

echo "This took $SECONDS seconds."
