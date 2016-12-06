# Load the appropriate modules and output the present versions.
set +x
module load GCCcore/.5.4.0
module load Autotools
module list
set -x

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

print-fancy-heading() {
    set +x
    echo "######################################################################"
    echo "# $*"
    echo "######################################################################"
    set -x
}

autoreconf-if-needed() {
    if ! [[ -f configure ]]; then
        aclocal
        autoreconf -f
        automake --add-missing
    fi
}

# Basic flags that are used for every single project compiled.
prefix="$HOME/local-jureca"
mkdir -p "$prefix"

build="$HOME/build-jureca"
mkdir -p "$build"

PATH=$prefix/bin:$PATH

compiler=${COMPILER-icc}

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
        base_flags="-O2 -Wall -H"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
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
        base_flags="-O2 -finline-limit=50000 -Wall -Wpedantic -fmax-errors=1 $color_flags -H"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        ;;
    *)
        echo "This compiler is not supported by this script. Choose another one."
        exit 1
        ;;
esac

cc=$(which $cc_name)
cxx=$(which $cxx_name)

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix --disable-shared --enable-static CC=$cc CXX=$cxx"
