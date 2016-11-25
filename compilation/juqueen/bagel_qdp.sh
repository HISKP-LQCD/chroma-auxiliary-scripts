clone-if-needed https://github.com/usqcd-software/bagel_qdp.git bagel_qdp master

pushd bagel_qdp
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then
    automake --add-missing
    autoreconf -f
fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-target-cpu=bgl \
        --with-bagel=$prefix \
        --with-qdp=$prefix \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
