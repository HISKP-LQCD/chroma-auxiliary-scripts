repo=qphix

print-fancy-heading $repo

clone-if-needed https://github.com/martin-ueding/qphix.git $repo ndtm

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
        --enable-proc=AVX \
        --enable-soalen=2 \
        --enable-clover \
        --enable-openmp \
        --disable-mm-malloc \
        --enable-parallel-arch=scalar \
        --with-qdp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
pushd include
make-make-install
popd
pushd lib
make-make-install
popd
popd
