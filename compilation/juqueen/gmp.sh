if ! [[ -d gmp-6.1.1 ]]; then
    wget https://gmplib.org/download/gmp/gmp-6.1.1.tar.xz
    tar -xf gmp-6.1.1.tar.xz
fi

pushd gmp-6.1.1
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        CFLAGS="$cflags"
fi
make-make-install
popd
