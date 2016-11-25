clone-if-needed https://github.com/martin-ueding/chroma.git chroma submodules-via-https

pushd chroma
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
if ! [[ -f configure ]]; then ./autogen.sh; fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-bgq-thread-binding \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --with-gmp="$prefix" \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qdp="$prefix" \
        --with-bagel-wilson-dslash=$prefix \
        --with-bagel-clover=$prefix \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
