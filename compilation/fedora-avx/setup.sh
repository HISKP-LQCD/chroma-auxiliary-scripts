# Basic flags that are used for every single project compiled.
compiler=${COMPILER-gcc}

case $compiler in
    gcc)
        cc_name=gcc
        cxx_name=g++
        color_flags="-fdiagnostics-color=auto"
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -fmax-errors=1 $color_flags -mavx"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        qphix_flags="-Drestrict=__restrict__"
        qphix_configure=""
        ;;
    *)
        echo "This compiler is not supported by this script. Choose another one."
        exit 1
        ;;
esac

playground=/home/mu/Dokumente/Studium/Master_Science_Physik/Masterarbeit/US_QCD/playground

prefix="$playground/local-$compiler"
mkdir -p "$prefix"

build="$playground/build-$compiler"
mkdir -p "$build"

sourcedir="$playground/sources"
mkdir -p "$sourcedir"
cd "$sourcedir"

PATH=$prefix/bin:$PATH

cc=$(which $cc_name)
cxx=$(which $cxx_name)

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix --disable-shared --enable-static CC=$cc CXX=$cxx"
