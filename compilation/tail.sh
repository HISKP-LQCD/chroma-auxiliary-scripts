
###############################################################################
#                              Environment Setup                              #
###############################################################################

# With `set -x`, Bash will output all commands that are run. This changes the
# output such that the number of seconds is printed out with each line. This
# will give some feeling for the time it needs to compile.
PS4='+[${SECONDS}s] '

if [[ "$_arg_verbose" = on ]]; then
  set -x
fi

# Create the target directory and then store the absolute path to this
# directory. Many compilation scripts have issues with linking to relative
# paths.
mkdir -p "$_arg_basedir"
pushd "$_arg_basedir"
basedir="$PWD"
popd

# Directory where the git repositories reside.
sourcedir="$basedir/sources"
mkdir -p "$sourcedir"

# Set all locale to C, such that compiler error messages are all in English.
# This makes debugging way easier because you can search for the messages
# online.
export LC_ALL=C

###############################################################################
#                                  Download                                   #
###############################################################################

# Download is done as an early step. This allows users to download all the
# needed files on a different machine as internet access is blocked on machines
# like Hazel Hen.

pushd "$sourcedir"

# CMake
#repo=cmake
#url=https://cmake.org/files/v3.9/cmake-3.9.1.tar.gz
#if ! [[ -d "$repo" ]]; then
#  if ! [[ -f "${url##*/}" ]]; then
#    wget "$url"
#  fi
#  tar -xf "${url##*/}"
#  mv cmake-3.9.1 cmake
#fi

# QMP
repo=qmp
clone-if-needed https://github.com/usqcd-software/qmp.git $repo master

# libxml2
repo=libxml2
clone-if-needed https://git.gnome.org/browse/libxml2 $repo v2.9.4

# LLVM
repo=llvm
url=http://releases.llvm.org/6.0.0/llvm-6.0.0.src.tar.xz
basename="${url##*/}"
if ! [[ -d "$repo" ]]; then
  if ! [[ -f "$basename" ]]; then
    wget "$url"
  fi
  tar -xf "$basename"
  mv llvm-6.0.0 "$repo"
fi

# QDP++
if [[ "$_arg_qdpjit" = off ]]; then
  repo=qdpxx
  clone-if-needed https://github.com/usqcd-software/qdpxx.git $repo devel
else
  repo=qdp-jit
  clone-if-needed https://github.com/fwinter/qdp-jit.git $repo master
fi

# QPhiX
repo=qphix
clone-if-needed https://github.com/JeffersonLab/qphix.git $repo "$_arg_qphix_branch"

# GNU MP
repo=gmp
if ! [[ -d "$repo" ]];
then
  # The upstream website only has a download as an LZMA compressed file. The
  # CentOS does not provide an `lzip` command. Also, there is no module
  # available that would supply it. Building `lzip` from source seems like a
  # waste of effort. Therefore I have just repacked that on my local machine
  # and uploaded to my webspace.
  url=http://bulk.martin-ueding.de/gmp-6.1.2.tar.gz
  #url=https://gmplib.org/download/gmp/gmp-6.1.2.tar.lz

  wget "$url"
  tar -xf "${url##*/}"
  mv gmp-6.1.2 gmp
fi

# Chroma
repo=chroma
clone-if-needed https://github.com/JeffersonLab/chroma.git $repo "$_arg_chroma_branch"

if [[ "$_arg_download_only" = on ]]; then
  set +x
  echo "User wanted do download only, we are done here."
  exit 0
fi

popd

###############################################################################
#                           Compiler Flag Selection                           #
###############################################################################

# Determine the fully qualified hostname and then set the optimal default
# compiler for the architecture found.
hostname_f="$(hostname -f)"

if [[ "$_arg_autodetect_machine" = off ]]; then
  if [[ -z "$_arg_isa" ]]; then
    echo "Builds on local machines require the -i option to be passed (ISA: avx, avx2, avx512)"
    exit 1
  fi
  host=local
  isa=$_arg_isa
  compiler="${_arg_compiler:-gcc}"
else
  if [[ "$hostname_f" =~ eslogin[0-9]+ ]]; then
    host=hazelhen
    isa=avx2
    compiler="${_arg_compiler:-icc}"
  elif [[ "$hostname_f" =~ [^.]*\.jureca ]]; then
    if [[ "${LMOD_SYSTEM_NAME-}" = jurecabooster ]]; then
      host=jurecabooster
      isa=avx512
    else
      host=jureca
      isa=avx2
    fi
    compiler="${_arg_compiler:-icc}"
  elif [[ "$hostname_f" =~ [^.]*\.marconi.cineca.it ]]; then
    if [[ -n "${ENV_KNL_HOME-}" ]]; then
      host=marconi-a2
      isa=avx512
      compiler="${_arg_compiler:-icc}"
    else
      set +x
      echo 'You seem to be running on Marconi but the environment variable ENV_KNL_HOME is not set. This script currently only supports Marconi A2, so please do `module load env-knl` to select the KNL partition.'
      exit 1
    fi
  else
    set +x
    echo "This machine is neither explicitly a 'local' machine nor JURECA nor Hazel Hen nor Marconi A2. It is not clear what should be done, please update the script."
    exit 1
  fi
fi

# Set up the chosen compiler.
case "$compiler" in
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
    color_flags=""
    openmp_flags="-fopenmp"
    c99_flags="-std=c99"
    cxx11_flags="-std=c++11"
    disable_warnings_flags="-Wno-all -Wno-pedantic -diag-disable 1224"
    qphix_flags="-restrict"
    # QPhiX can make use of the Intel “C Extended Array Notation”, this
    # gets enabled here.
    qphix_configure="--enable-cean"

    case "$host" in
      jureca)
        checked-module load Intel/2017.2.174-GCC-5.4.0
        checked-module load IntelMPI/2017.2.174
        silent module list
        cc_name=mpiicc
        cxx_name=mpiicpc
        host_cxx=icpc
        base_flags="-xAVX2 -O3"
        ;;
      jurecabooster)
        checked-module load Intel/2018.1.163-GCC-5.4.0
        checked-module load IntelMPI/2018.1.163
        checked-module load CMake
        silent module list
        cc_name=mpiicc
        cxx_name=mpiicpc
        host_cxx=icpc
        base_flags="-xMIC-AVX512 -O3"
        ;;
      hazelhen)
        # On Hazel Hen, the default compiler is the Cray compiler. One needs to
        # unload that and load the Intel programming environment. That should
        # also load the Intel MPI implementation.
        checked-module swap PrgEnv-cray PrgEnv-intel
        checked-module load intel/17.0.6.256
        silent module list
        # On this system, the compiler is always the same because the module
        # system loads the right one of these wrappers.
        cc_name=cc
        cxx_name=CC
        host_cxx=icpc
        base_flags="-xAVX2 -O3"
        ;;
      marconi-a2)
        checked-module load intel/pe-xe-2017--binary
        checked-module load intelmpi
        silent module list
        cc_name=mpiicc
        cxx_name=mpiicpc
        host_cxx=icpc
        base_flags="-xMIC-AVX512 -O3"
        ;;
      *)
        set +x
        echo "Compiler ICC is not supported on $host."
        exit 1
    esac
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
        checked-module load GCC
        checked-module load ParaStationMPI
        silent module list
        cc_name=mpicc
        cxx_name=mpic++
        host_cxx=g++
        base_flags="-O3 -finline-limit=50000 $color_flags -march=haswell"
        ;;
      hazelhen)
        silent module swap PrgEnv-cray PrgEnv-gnu
        silent module list
        cc_name=cc
        cxx_name=CC
        host_cxx=g++
        base_flags="-O3 -finline-limit=50000 $color_flags -march=haswell"
        ;;
      marconi-a2)
        checked-module load gnu
        checked-module load ParaStationMPI
        silent module list
        cc_name=mpicc
        cxx_name=mpic++
        host_cxx=g++
        base_flags="-O3 -finline-limit=50000 -fmax-errors=1 $color_flags -march=knl"
        ;;
      local)
        cc_name=mpicc
        cxx_name=mpic++
        host_cxx=g++
        base_flags="-O3 -finline-limit=50000 -fmax-errors=1 $color_flags -march=native"
        ;;
      *)
        set +x
        echo "Compiler GCC is not supported on $host."
        exit 1
    esac
    ;;
  *)
    echo 'This compiler is not supported by this script. Choose another one or add another block to the `case` in this script.'
    exit 1
    ;;
esac

# Directory for the installed files (headers, libraries, executables). This
# contains the chosen compiler in the dirname such that multiple compilers can
# be used simultaneously.
prefix="$basedir/local-$compiler"
mkdir -p "$prefix"

# Directory for building. The GNU Autotools support out-of-tree builds which
# allow to use different compilers on the same codebase.
build="$basedir/build-$compiler"
mkdir -p "$build"

# The GNU Autotools install `X-config` programs that let a dependent library
# query the `CFLAGS` and `CXXFLAGS` used in the compilation. This needs to be
# in the `$PATH`, otherwise libraries cannot be found properly. In principle it
# should be sufficient to pass the installation path to the `configure` scripts
# but this has not always worked properly, therefore this additional thing.
# Additionally we might install auxiliary software like CMake on some systems,
# we want it to be preferred over the system-wide installed versions.
PATH=$prefix/bin:$PATH

# Basic flags that will be used for all compilations. The full path to the C
# and C++ compiler are queried here and stored. Changes in modules later on
# will not alter the compilers, therefore.
base_cxxflags="$base_flags"
base_cflags="$base_flags $c99_flags"
base_configure="--prefix=$prefix CC=$(which $cc_name) CXX=$(which $cxx_name) --enable-option-checking"

case "$host" in
  hazelhen)
    # The “huge pages” are used on Hazel Hen. This leads to the inability to run
    # execute programs on the login nodes that are compiled with the MPI compiler
    # wrapper. Autotools need to be told that it cross compiles such that the
    # `./configure` script won't try to execute the test programs.
    base_configure="$base_configure --host=x86_64-linux-gnu"
    ;;
  jurecabooster|marconi-a2)
    # Marconi A2 has a cross compilation from Haswell to Knights Landing,
    # therefore one needs to tell GNU Autotools that programs compiled with the
    # target compiler cannot be executed on the host.
    base_configure="$base_configure --host=x86_64-linux-gnu"
    ;;
esac

cd "$sourcedir"

###############################################################################
#                                    CMake                                    #
###############################################################################

# Hazel Hen only has version 2.6 of CMake which is too old for us. There is a
# newer version, but that can only be used when the GNU compiler is loaded. It
# does not work with the Intel compiler. Trying to find the path of the modern
# version of CMake works, but then it cannot load the GNU standard library,
# *sigh*.
#
# I have contacted the support on 2017-08-21 and they will provide a more
# modern version of CMake that can be used with the Intel compiler. For the
# meantime, we install CMake ourselves here and use that.

#repo=cmake
#print-fancy-heading $repo
#
#case "$host" in
#  hazelhen)
#    pushd "$repo"
#    if ! [[ -f Makefile ]]; then
#      ./bootstrap --prefix="$prefix"
#    fi
#    make-make-install
#    popd
#    ;;
#esac

###############################################################################
#                                     QMP                                     #
###############################################################################

repo=qmp
print-fancy-heading $repo

cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"

pushd $repo
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

case "$host" in
  jureca|marconi-a2)
    cflags="$base_cflags"
    cxxflags="$base_cxxflags"

    pushd $repo
    if ! [[ -f configure ]]; then
      mkdir -p m4
      pushd m4
      ln -fs /usr/share/aclocal/pkg.m4 .
      popd
      checked-module load Autotools
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
    cflags="$base_cflags"
    cxxflags="$base_cxxflags"

    pushd $repo
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

    libxml="$prefix/bin/xml2-config"
    ;;
  local)
    libxml="/usr/include/libxml2"
    ;;
esac

###############################################################################
#                                    QDP++                                    #
###############################################################################

if [[ "$_arg_qdpjit" = off ]]; then
  repo=qdpxx
  print-fancy-heading $repo

  cflags="$base_cflags $openmp_flags"
  cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"

  pushd $repo
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
      --enable-precision=$_arg_precision \
      --with-libxml2="$libxml" \
      --with-qmp="$prefix" \
      CFLAGS="$cflags" CXXFLAGS="$cxxflags"
  fi
  make-make-install
  popd
fi

###############################################################################
#                                   QDP-JIT                                   #
###############################################################################

exit

if [[ "$_arg_qdpjit" = on ]]; then
fi

###############################################################################
#                                    QPhiX                                    #
###############################################################################

repo=qphix
print-fancy-heading $repo

case $host in
  jureca)
    checked-module load CMake
    checked-module load Python
    ;;
  hazelhen)
    checked-module load tools/python

    python_library=/opt/hlrs/tools/python/anaconda3-4.2.0/lib/libpython3.so
    python_include_dir=/opt/hlrs/tools/python/anaconda3-4.2.0/include
    ;;
  marconi-a2)
    checked-module load cmake
    checked-module load python
    ;;
esac

set +x
if [[ "$host" != "local" ]]; then
  module list
fi
set -x

# Check whether Python 3 interpreter is there. The following calls Python 3 and
# lets it do explicitly nothing. That must always work. Then we output the path
# for reference.
python3 -c ''
which python3

cxxflags="$base_cxxflags $openmp_flags $cxx11_flags $qphix_flags"
cxx=$(which $cxx_name)

# Due to the module system, the `python3` executable can be found in the
# `$PATH`, but somehow CMake cannot find what it needs. Therefore we need to
# set those paths manually. Fortunately we can [use Python to give this to
# us](https://stackoverflow.com/a/38121972) and pass that on to CMake.
cmake_python_include_dir="$(python3 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())")"
cmake_python_library="$(python3 -c "import distutils.sysconfig as sysconfig; print(sysconfig.get_config_var('LIBDIR'))")"

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
  cxx=$(which $cxx_name)
  CXX=$cxx CXXFLAGS="$cxxflags" \
    cmake -Disa=$isa \
    -Dhost_cxx="$host_cxx" \
    -Dhost_cxxflags="$cxx11_flags" \
    -Drecursive_jN=$(nproc) \
    -DCMAKE_INSTALL_PREFIX="$prefix" \
    -DQDPXX_DIR="$prefix" \
    -Dclover=TRUE \
    -Dtwisted_mass=TRUE \
    -Dtm_clover=TRUE \
    -Dcean=FALSE \
    -Dmm_malloc=TRUE \
    -Dtesting=TRUE \
    -DPYTHON_INCLUDE_DIR="$cmake_python_include_dir"  \
    -DPYTHON_LIBRARY="$cmake_python_library" \
    $sourcedir/$repo
fi
make-make-install
popd

if [[ "$_arg_only_qphix" = "true" ]]; then
  echo "QPhiX is installed, user wished to abort here."
  exit 0
fi

###############################################################################
#                             GNU Multi Precision                             #
###############################################################################

repo=gmp
print-fancy-heading $repo

case "$host" in
  jureca)
    set +x
    checked-module load GMP
    set -x
    gmp="$EBROOTGMP"
    ;;
  hazelhen)
    gmp="-lgmp"
    ;;
  marconi-a2)
    # The GNU MP library installed on the Marconi system, but it might be
    # linked against an older version of the standard library. Therefore we
    # compile it from scratch.

    repo=gmp
    print-fancy-heading $repo

    cflags="$base_cflags"
    cxxflags="$base_cxxflags"

    pushd "$repo"
    autoreconf-if-needed
    popd

    mkdir -p "$build/$repo"
    pushd "$build/$repo"
    if ! [[ -f Makefile ]]; then
      $sourcedir/$repo/configure $base_configure \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
    fi
    make-make-install
    popd

    gmp="$prefix"
    ;;
esac

###############################################################################
#                                   Chroma                                    #
###############################################################################

repo=chroma
print-fancy-heading $repo

cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"

pushd $repo
autoreconf-if-needed
popd

# Select a default SoA length.
case "$host" in
  jureca|hazelhen)
    soalen=4
    inner_soalen=4
    ;;
  marconi-a2)
    soalen=8
    inner_soalen=4
    ;;
esac

# Overwrite with the value that the user has chosen, if it is set.
soalen=${_arg_soalen-$soalen}
inner_soalen=${_arg_soalen_inner-$inner_soalen}

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
  $sourcedir/$repo/configure $base_configure \
    --enable-openmp \
    --enable-parallel-arch=parscalar \
    --enable-parallel-io \
    --enable-precision=$_arg_precision \
    --enable-qdp-alignment=128 \
    --enable-sse2 \
    --with-gmp="$gmp" \
    --with-libxml2="$libxml" \
    --with-qdp="$prefix" \
    --with-qphix-solver="$prefix" \
    --enable-qphix-solver-compress12 \
    --enable-qphix-solver-arch=$isa \
    --enable-qphix-solver-soalen=$soalen \
    --enable-qphix-solver-inner-soalen=$inner_soalen \
    --enable-qphix-solver-inner-type=$_arg_precision_inner \
    CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

echo
echo "That took $SECONDS seconds."

# vim: spell sts=2 sw=2
