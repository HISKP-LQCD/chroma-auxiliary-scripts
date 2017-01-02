# Load the appropriate modules and output the present versions.
set +x
module load GCCcore/.5.4.0
module load Autotools
module list
set -x

# Basic flags that are used for every single project compiled.
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
        base_flags="-O2"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        qphix_flags="-xAVX -qopt-report -qopt-report-phase=vec -restrict"
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
        base_flags="-O2 -finline-limit=50000 -fmax-errors=1 $color_flags"
        cxx11_flags="--std=c++11"
        disable_warnings_flags="-Wno-all -Wno-pedantic"
        qphix_flags="-Drestrict=__restrict__ -mavx2"
        qphix_configure=""
        ;;
    *)
        echo "This compiler is not supported by this script. Choose another one."
        exit 1
        ;;
esac

prefix="$HOME/jureca-local-$compiler"
mkdir -p "$prefix"

build="$HOME/jureca-build-$compiler"
mkdir -p "$build"

PATH=$prefix/bin:$PATH

cc=$(which $cc_name)
cxx=$(which $cxx_name)

base_cxxflags="$base_flags"
base_cflags="$base_flags"
base_configure="--prefix=$prefix --disable-shared --enable-static CC=$cc CXX=$cxx"
