repo=qdpxx

print-fancy-heading $repo

clone-if-needed https://github.com/martin-ueding/qdpxx.git $repo martins-fedora24-build

pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-openmp \
        --enable-sse --enable-sse2 \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

