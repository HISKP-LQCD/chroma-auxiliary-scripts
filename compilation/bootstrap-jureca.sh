#!/bin/bash
# Copyright © 2016-2017 Martin Ueding <dev@martin-ueding.de>

# Installs US QCD Chroma on JURECA, an Intel Xeon E5-2680 v3 Haswell + NVIDIA
# K40 supercomputer.

# License (MIT/Expat)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -e
set -u
set -x

# Force the user specify a directory where everything should be put into.
if (( $# == 0 )); then
    echo "usage: $0 BASE"
fi
basedir="$PWD/$1"

# Set all locale to C, such that compiler error messages are all in English.
# This makes debugging way easier.
export LC_ALL=C

# Load the appropriate modules and output the present versions.
set +x
module load GCCcore/.5.4.0
module load Autotools
module list
set -x

# The best compiler for JURECA is the Intel C++. You can choose a different
# compiler setting the environment `COMPILER` variable when calling this
# script.
compiler=${COMPILER-icc}

# Set up the chosen compiler.
case $compiler in
    icc)
        set +x
        module load Intel/2017.0.098-GCC-5.4.0
        module load IntelMPI/2017.0.098
        module list
        set -x
        cc_name=mpiicc
        cxx_name=mpiicpc
        color_flags=""
        openmp_flags="-fopenmp"
        base_flags="-O2"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        qphix_flags="-xAVX -qopt-report -qopt-report-phase=vec -restrict"
        # QPhiX can make use of the Intel “C Extended Array Notation”, this
        # gets enabled here.
        qphix_configure="--enable-cean"
        ;;
    gcc)
        set +x
        module load GCC
        module load ParaStationMPI
        module list
        set -x
        cc_name=mpicc
        cxx_name=mpic++
        color_flags="-fdiagnostics-color=auto"
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -fmax-errors=1 $color_flags -mavx2"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        qphix_flags="-Drestrict=__restrict__"
        qphix_configure=""
        ;;
    *)
        echo 'This compiler is not supported by this script. Choose another one or add another block to the `case` in this script.'
        exit 1
        ;;
esac

# Directory where the git repositories reside.
sourcedir="$basedir/sources"
mkdir -p "$sourcedir"

# Directory for the installed files (headers, libraries, executables). This
# contains the chosen compiler such that multiple compilers can be used
# simultaneously.
prefix="$basedir/local-$compiler"
mkdir -p "$prefix"

# Directory for building. The GNU Autotools support out-of-tree builds which
# allow to use different compilers on the same codebase.
build="$basedir/build-$compiler"
mkdir -p "$build"

# The GNU Autotools install `X-config` programs that let a dependent library
# query the `CFLAGS` and `CXXFLAGS` used in the compilation. This needs to be
# in the `$PATH`, otherwise libraries cannot be found properly.
PATH=$prefix/bin:$PATH

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix --disable-shared --enable-static CC=$(which $cc_name) CXX=$(which $cxx_name)"

# Clones a git repository if the directory does not exist. It does not call
# `git pull`. After cloning, it deletes the `configure` and `Makefile` that are
# shipped by default such that they get regenerated in the next step.
clone-if-needed() {
    local url="$1"
    local dir="$2"
    local branch="$3"

    if ! [[ -d "$dir" ]]
    then
        git clone "$url" --recursive -b "$branch"

        pushd "$dir"
        rm -f configure Makefile
        popd
    fi
}

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.
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

# If the user has not given a variable `SMP` in the environment, use as many
# processes to compile as there are cores in the system.
make_smp_template="-j $(nproc)"
make_smp_flags="${SMP-$make_smp_template}"

# Prints a large heading such that it is clear where one is in the compilation
# process. This is not needed but occasionally helpful.
print-fancy-heading() {
    set +x
    echo "######################################################################"
    echo "# $*"
    echo "######################################################################"
    set -x

    if [[ -d "$sourcedir/$repo" ]]; then
        pushd "$sourcedir/$repo"
        git branch
        popd
    fi
}

# I have not fully understood this here. I *feel* that there is some cyclic
# dependency between `automake --add-missing` and the `autoreconf`. It does not
# make much sense. Perhaps one has to split up the `autoreconf` call into the
# parts that make it up. Using this weird dance, it works somewhat reliably.
autotools-dance() {
    automake --add-missing --copy || autoreconf -f || automake --add-missing --copy
    autoreconf -f
}

# Invokes the various commands that are needed to update the GNU Autotools
# build system. Since the submodules are also Autotools projects, these
# commands need to be invoked from the bottom up, recursively. The regular `git
# submodule foreach` will do a traversal from the top. Due to the nested nature
# of the GNU Autotools, we need to have depth-first traversal. Assuming that
# the directory names do not have anything funny in them, the parsing of the
# output can work.
autoreconf-if-needed() {
    if ! [[ -f configure ]]; then
        if [[ -f .gitmodules ]]; then
            for module in $(git submodule foreach --quiet --recursive pwd | tac); do
                pushd "$module"
                aclocal
                autotools-dance
                popd
            done
        fi

        aclocal
        autotools-dance
    fi
}

cd "$sourcedir"

###############################################################################
#                                     QMP                                     #
###############################################################################

repo=qmp
print-fancy-heading $repo
clone-if-needed https://github.com/usqcd-software/qmp.git $repo master

pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        --with-qmp-comms-type=MPI \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                                   libxml2                                   #
###############################################################################

repo=libxml2
print-fancy-heading $repo
clone-if-needed git://git.gnome.org/libxml2 $repo v2.9.4

pushd $repo
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then
    mkdir -p m4
    pushd m4
    ln -fs /usr/share/aclocal/pkg.m4 .
    popd
    NOCONFIGURE=yes ./autogen.sh
fi
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
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
#                                    QDP++                                    #
###############################################################################

repo=qdpxx
print-fancy-heading $repo
clone-if-needed https://github.com/usqcd-software/qdpxx.git $repo devel

pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        --enable-openmp \
        --enable-sse --enable-sse2 \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

###############################################################################
#                                    QPhiX                                    #
###############################################################################

repo=qphix
print-fancy-heading $repo
clone-if-needed https://github.com/JeffersonLab/qphix.git $repo devel

pushd $repo
cflags="$base_cflags $openmp_flags $qphix_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags $qphix_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        $qphix_configure \
        --disable-testing \
        --enable-proc=AVX2 \
        --enable-soalen=4 \
        --enable-clover \
        --enable-openmp \
        --enable-mm-malloc \
        --enable-parallel-arch=parscalar \
        --with-qdp="$prefix" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi

# In the current version, the tests to do not build. This is not a problem as
# they are not needed to run Chroma. Compiling and installing the include files
# and libraries is enough.
pushd include
make-make-install
popd
pushd lib
make-make-install
popd
popd

###############################################################################
#                                   Chroma                                    #
###############################################################################

repo=chroma
print-fancy-heading $repo
clone-if-needed https://github.com/JeffersonLab/chroma.git $repo devel

set +x
module load GMP
set -x

pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --enable-sse2 \
        --enable-qphix-solver-arch=avx \
        --with-gmp="$EBROOTGMP" \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qdp="$prefix" \
        --with-qphix-solver="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

# vim: spell
