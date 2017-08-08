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
if (( $# == 0 )) || [[ ${1:0:1} = - ]]; then
    cat <<EOF
This is a script to install Chroma, QPhiX, QDP++, QMP, and their dependencies
on the Intel Knights Landing based supercomputer “Marconi A2” hosted by CINECA
in Casalecchio di Reno, Italy.

Usage: $0 BASE

BASE is the directory where everthing is downloaded, compiled, and installed.
After this script ran though, you will have the following directories:

BASE/build-icc/qmp
BASE/build-icc/qphix
BASE/build-icc/qdpxx
BASE/build-icc/chroma
BASE/build-icc/libxml2

BASE/local-icc/include
BASE/local-icc/bin
BASE/local-icc/lib
BASE/local-icc/share

BASE/sources/qmp
BASE/sources/qphix
BASE/sources/qdpxx
BASE/sources/chroma
BASE/sources/libxml2
EOF
    exit 1
fi

mkdir -p "$1"
pushd "$1"
basedir="$PWD"
popd

# Set all locale to C, such that compiler error messages are all in English.
# This makes debugging way easier.
export LC_ALL=C

# The `module load` command does not set the exit status when it fails. Also it
# annoyingly outputs everything on standard error. This function parses the
# output and checks for the word `error` case insensitively. The function will
# then fail.
checked-module-load() {
  set +x
  echo "+ module load $1"
  module load $1 2>&1 > module-load-output.txt
  set -x
  cat module-load-output.txt
  if grep -i error module-load-output.txt; then
    echo "There has been some error while loading module $1, aborting"
    exit 1
  fi
  rm -f module-load-output.txt
}

# Set all locale to C, such that compiler error messages are all in English.
# This makes debugging way easier.
export LC_ALL=C

hostname_f="$(hostname -f)"

if [[ "$hostname_f" =~ [^.]*\.hww\.de ]]; then
  host=hazelhen
  compiler="${COMPILER-icc}"
elif [[ "$hostname_f" =~ [^.]*\.jureca ]]; then
  host=jureca
  compiler="${COMPILER-icc}"
elif [[ "$hostname_f" =~ [^.]*\.marconi.cineca.it ]]; then
  if [[ -n "$ENV_KNL_HOME" ]]; then
    host=marconi-a2
    compiler="${COMPILER-icc}"
  else
    echo 'You seem to be running on Marconi but the environment variable ENV_KNL_HOME is not set. This script currently only supports Marconi A2, so please do `module load env-knl` to select the KNL partition.'
    exit 1
  fi
else
  set +x
  echo "This machine is neither JURECA nor Hazel Hen nor Marconi A2. It is not clear which compiler to use. Set the environment variable 'COMPILER' to 'cray', 'icc' or 'gcc'."
  exit 1
fi


# Set up the chosen compiler.
case $compiler in
  # The cray compiler does not support half-precision data types (yet). So
  # one cannot actually use that for QPhiX right now.
  cray)
    cc_name=cc
    cxx_name=CC
    color_flags=""
    openmp_flags=""
    base_flags="-O2 -hcpu=haswell"
    c99_flags="-hstd=c99"
    cxx11_flags="-hstd=c++11"
    disable_warnings_flags=""
    qphix_flags=""
    qphix_configure=""
    ;;
  icc)
    case "$host" in
      jureca)
        set +x
        checked-module-load Intel/2017.2.174-GCC-5.4.0
        checked-module-load IntelMPI/2017.2.174
        module list
        set -x
        cc_name=mpiicc
        cxx_name=mpiicpc
        base_flags="-xAVX2 -O3"
        ;;
      hazelhen)
        set +x
        # On Hazel Hen, the default compiler is the Cray compiler. One needs to
        # unload that and load the Intel programming environment. That should
        # also load the Intel MPI implementation.
        module swap PrgEnv-cray PrgEnv-intel
        # If one does not load a newer GCC version, the modern Intel compiler
        # will use the GCC 4.3 standard library. That however does not support
        # C++11 such that it will not work.
        checked-module-load gcc/6.3.0
        checked-module-load intel/17.0.2.174
        module list
        set -x
        # On this system, the compiler is always the same because the module
        # system loads the right one of these wrappers.
        cc_name=cc
        cxx_name=CC
        base_flags="-xAVX2 -O3"
        ;;
      marconi-a2)
        set +x
        checked-module-load intel/pe-xe-2017--binary
        checked-module-load intelmpi
        module list
        set -x
        cc_name=mpiicc
        cxx_name=mpiicpc
        base_flags="-xMIC-AVX512 -O3"
        ;;
    esac

    color_flags=""
    openmp_flags="-fopenmp"
    c99_flags="-std=c99"
    cxx11_flags="-std=c++11"
    disable_warnings_flags="-Wno-all -Wno-pedantic -diag-disable 1224"
    qphix_flags="-restrict"
    # QPhiX can make use of the Intel “C Extended Array Notation”, this
    # gets enabled here.
    qphix_configure="--enable-cean"
    ;;
  gcc)
    color_flags="-fdiagnostics-color=auto"
    openmp_flags="-fopenmp"
    c99_flags="--std=c99"
    cxx11_flags="--std=c++11"
    disable_warnings_flags="-Wno-all -Wno-pedantic"
    qphix_flags="-Drestrict=__restrict__"
    qphix_configure=""

    case "$host" in
      jureca)
        set +x
        checked-module-load GCC
        checked-module-load ParaStationMPI
        module list
        set -x
        cc_name=mpicc
        cxx_name=mpic++
        base_flags="-O3 -finline-limit=50000 $color_flags -march=haswell"
        ;;
      hazelhen)
        set +x
        module swap PrgEnv-cray PrgEnv-gnu
        module list
        set -x
        cc_name=cc
        cxx_name=CC
        base_flags="-O3 -finline-limit=50000 $color_flags -march=haswell"
        ;;
      marconi-a2)
        set +x
        checked-module-load gnu
        checked-module-load ParaStationMPI
        module list
        set -x
        cc_name=mpicc
        cxx_name=mpic++
        base_flags="-O3 -finline-limit=50000 -fmax-errors=1 $color_flags -march=knl"
        ;;
    esac
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
base_cflags="$base_flags $c99_flags"
base_configure="--prefix=$prefix CC=$(which $cc_name) CXX=$(which $cxx_name)"

case hostname in
  hazelhen)
    # The “huge pages” are used on Hazel Hen. This leads to the inability to run
    # execute programs on the login nodes that are compiled with the MPI compiler
    # wrapper. Autotools need to be told that it cross compiles such that the
    # `./configure` script won't try to execute the test programs.
    base_configure="$base_configure --host=x86_64-linux-gnu"
    ;;
  marconi-a2)
    # Marconi A2 has a cross compilation from Haswell to Knights Landing,
    # therefore one needs to tell GNU Autotools that programs compiled with the
    # target compiler cannot be executed on the host.
    base_configure="$base_configure --host=x86_64-linux-gnu"
    ;;
esac

# Clones a git repository if the directory does not exist. It does not call
# `git pull`. After cloning, it deletes the `configure` and `Makefile` that are
# shipped by default such that they get regenerated in the next step.
clone-if-needed() {
  local url="$1"
  local dir="$2"
  local branch="$3"

  if ! [[ -d "$dir" ]]; then
    case "$host" in
      hazelhen)
        cat<<EOF
The git repository for “$dir” could not be found, it has to be cloned.
Unfortunately outgoing HTTPS connections as needed for “git clone” are blocked
by the firewall. You will have to download the repository yourself. Execute the
following commands:

    cd "$PWD"
    git clone "$url" --recursive -b "$branch"
    rm -f configure Makefile
EOF
        ;;
      *)
        git clone "$url" --recursive -b "$branch"

        pushd "$dir"
        if [[ -f Makefile.am ]]; then
          rm -f Makefile
        fi
        rm -f configure
        popd
        ;;
    esac
  fi
}

# If the user has not given a variable `SMP` in the environment, use as many
# processes to compile as there are cores in the system.
make_smp_template="-j $(nproc)"
make_smp_flags="${SMP-$make_smp_template}"

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.
make-make-install() {
  if ! [[ -f build-succeeded ]]; then
    nice make $make_smp_flags VERBOSE=1
    make install VERBOSE=1
    touch build-succeeded
    pushd $prefix/lib
    rm -f *.so *.so.*
    popd
  fi
}

# Prints a large heading such that it is clear where one is in the compilation
# process. This is not needed but occasionally helpful.
print-fancy-heading() {
  set +x
  echo "######################################################################"
  echo "# $*"
  echo "######################################################################"
  set -x

  if [[ -d "$sourcedir/$repo/.git" ]]; then
    pushd "$sourcedir/$repo"
    git branch
    popd
  fi
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
        autoreconf -vif
        popd
      done
    fi

    aclocal
    autoreconf -vif
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

case hostname in
  jureca|marconi-a2)
    repo=libxml2
    print-fancy-heading $repo
    clone-if-needed https://git.gnome.org/browse/libxml2 $repo v2.9.4

    pushd $repo
    cflags="$base_cflags"
    cxxflags="$base_cxxflags"
    if ! [[ -f configure ]]; then
      mkdir -p m4
      pushd m4
      ln -fs /usr/share/aclocal/pkg.m4 .
      popd
      set +x
      checked-module-load Autotools
      set -x
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

    libxml="$prefix/bin/xml2-config"
    ;;
  hazelhen)
    libxml="/usr/include/libxml2"
    ;;
esac

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
    --with-libxml2="$libxml" \
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

case $host in
  jureca)
    checked-module-load CMake
    checked-module-load Python
    ;;
  hazelhen)
    # Hazel Hen has the quirk that a modern version of CMake can only be loaded
    # in the GNU programming environment. So here we switch to the GNU
    # environment, just to be able to _use_ a non-ancient version of CMake.
    set +x
    module swap PrgEnv-intel PrgEnv-gnu
    set -x
    checked-module-load tools/cmake
    checked-module-load tools/python
    set +x
    module list
    set -x

    python_library=/opt/hlrs/tools/python/anaconda3-4.2.0/lib/libpython3.so
    python_include_dir=/opt/hlrs/tools/python/anaconda3-4.2.0/include
    ;;
  marconi-a2)
    checked-module-load cmake
    checked-module-load python
    ;;
esac

set +x
module list
set -x

# Check whether Python 3 interpreter is there.
python3 -c ''
which python3

cxxflags="$base_cxxflags $openmp_flags $cxx11_flags $qphix_flags"
cxx=$(which $cxx_name)

# https://stackoverflow.com/a/38121972

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
  cxx=$(which $cxx_name)
  CXX=$cxx CXXFLAGS="$cxxflags" \
    cmake -Disa=avx2 \
    -Dhost_cxx="g++" \
    -Dhost_cxxflags="-g -O3 -std=c++11" \
    -Drecursive_jN=$(nproc) \
    -DCMAKE_INSTALL_PREFIX="$prefix" \
    -DQDPXX_DIR="$prefix" \
    -Dclover=TRUE \
    -Dtwisted_mass=TRUE \
    -Dtm_clover=TRUE \
    -Dcean=FALSE \
    -Dmm_malloc=TRUE \
    -Dtesting=TRUE \
    -DPYTHON_INCLUDE_DIR="$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")"  \
    -DPYTHON_LIBRARY="$(python3 -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")" \
    $sourcedir/$repo
fi
make-make-install
popd

case $host in
  hazelhen)
    # Now we have to get our target programming environment back.
    module swap PrgEnv-gnu PrgEnv-intel
    checked-module-load gcc/6.3.0
    checked-module-load intel/17.0.2.174
    ;;
esac


###############################################################################
#                             GNU Multi Precision                             #
###############################################################################

repo=gmp
print-fancy-heading $repo

case "$host" in
  jureca)
    set +x
    checked-module-load GMP
    set -x
    gmp="$EBROOTGMP"
    ;;
  hazelhen)
    gmp="-lgmp"
    ;;
  marconi-a2)
    checked-module-load gmp
    gmp="-lgmp"
    ;;
esac

###############################################################################
#                                   Chroma                                    #
###############################################################################

repo=chroma
print-fancy-heading $repo
clone-if-needed https://github.com/JeffersonLab/chroma.git $repo devel


pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
popd

case hostname in
  jureca|hazelhen)
    chroma_configure='--enable-qphix-solver-arch=avx2 --enable-qphix-solver-soalen=4'
    ;;
  marconi-a2)
    chroma_configure='--enable-qphix-solver-arch=avx512 --enable-qphix-solver-soalen=4'
    ;;
esac

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
    --with-gmp="$gmp" \
    --with-libxml2="$libxml" \
    --with-qdp="$prefix" \
    --with-qphix-solver="$prefix" \
    --enable-qphix-solver-compress12 \
    $chroma_configure \
    CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

echo
echo "That took $SECONDS seconds."

# vim: spell sts=2 sw=2
