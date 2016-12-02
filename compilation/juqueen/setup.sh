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

print-fancy-heading() {
    set +x
    echo "######################################################################"
    echo "# $*"
    echo "######################################################################"
    set -x
}

autoreconf-if-needed() {
    if ! [[ -f configure ]]; then
        if ! autoreconf -f
        then
            automake --add-missing
            autoreconf -f
        fi
    fi
}

# Basic flags that are used for every single project compiled.
prefix="$HOME/local-juqueen"
mkdir -p "$prefix"

build="$HOME/build-juqueen"
mkdir -p "$build"

PATH=$prefix/bin:$PATH

compiler=${COMPILER-clang}

case $compiler in
    ibmxl)
        cc_name=mpixlc_r
        cxx_name=mpixlcxx_r
        color_flags=""
        openmp_flags="-qsmp=omp -qnosave"
        base_flags="-qarch=qp -O2"
        cxx11_flags="-qlanglvl=extended0x"
        disable_warnings_flags=""
        ;;
    gcc-4.9)
        module load gcc/4.9.3
        cc_name=mpigcc
        cxx_name=mpig++
        color_flags="-fdiagnostics-color=auto"
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -Wall -Wpedantic -fmax-errors=1 $color_flags"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        ;;
    gcc-4.4)
        cc_name=mpigcc
        cxx_name=mpig++
        openmp_flags="-fopenmp"
        base_flags="-O2 -finline-limit=50000 -Wall -pedantic"
        cxx11_flags=""
        disable_warnings_flags=""
        ;;
    clang)
        module load clang/3.7.r236977
        cc_name=mpicc
        cxx_name=mpic++
        openmp_flags="-fopenmp"
        base_flags="-O2 -Wall -Wpedantic -ferror-limit=1"
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

cross_compile_flags="--host=powerpc64-bgq-linux --build=powerpc64-unknown-linux-gnu"
mpich_include_flags="-I/usr/local/bg_soft/mpich3/include"

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix $cross_compile_flags --disable-shared --enable-static CC=$cc CXX=$cxx"
