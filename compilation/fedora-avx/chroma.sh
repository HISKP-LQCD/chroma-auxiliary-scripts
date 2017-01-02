repo=chroma

print-fancy-heading $repo

clone-if-needed https://github.com/JeffersonLab/chroma.git $repo devel

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
        --enable-parallel-arch=scalar \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --enable-sse2 \
        --enable-qphix-solver-arch=avx \
        --with-gmp="/usr/include" \
        --with-libxml2="/usr/include" \
        --with-qdp="$prefix" \
        --with-qphix-solver="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
