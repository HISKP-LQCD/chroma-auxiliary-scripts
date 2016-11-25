print-fancy-heading qphix

clone-if-needed https://github.com/JeffersonLab/qphix.git qphix master

pushd qphix
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags $cxx11_flags"
autoreconf-if-needed
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --disable-mm-malloc \
        --disable-testing \
        --enable-clover \
        --enable-openmp \
        --enable-parallel-arch=parscalar \
        --with-qdp++="$prefix" \
        --with-qdp="$prefix" \
        --with-qmp="$prefix" \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
