print-fancy-heading chroma

clone-if-needed https://github.com/martin-ueding/chroma.git chroma submodules-via-https

set +x
module load GMP
set -x

pushd chroma
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --enable-parallel-io \
        --enable-precision=double \
        --enable-qdp-alignment=128 \
        --enable-sse2 \
        --with-gmp="$EBROOTGMP" \
        --with-libxml2="$prefix/bin/xml2-config" \
        --with-qdp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
