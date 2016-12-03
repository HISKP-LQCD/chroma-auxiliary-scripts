repo=qphix

print-fancy-heading $repo

clone-if-needed https://github.com/martin-ueding/qphix.git $repo master

pushd $repo
extra_common="-xAVX -qopt-report -qopt-report-phase=vec -restrict"
cflags="$base_cflags $openmp_flags $extra_common"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags $extra_common"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        --disable-testing \
        --enable-proc=AVX \
        --enable-soalen=4 \
        --enable-cean \
        --enable-clover \
        --enable-openmp \
        --enable-mm-malloc \
        --enable-parallel-arch=parscalar \
        --with-qdp="$prefix" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
