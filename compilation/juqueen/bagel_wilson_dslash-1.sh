wget-if-needed http://www2.ph.ed.ac.uk/~paboyle/bagel/bagel_wilson_dslash-1.4.6.tar.gz bagel_wilson_dslash-1.4.6

pushd bagel_wilson_dslash-1.4.6
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then autoreconf -f; fi
if ! [[ -f Makefile ]]; then
    CC=$cc CXX=$cxx ./configure $base_configure \
        --enable-comms=qmp \
        --enable-target-cpu=bgl \
        --with-bagel=$prefix \
        --with-qmp=$prefix \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
