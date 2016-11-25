print-fancy-heading bagel 1.4.0

wget-if-needed http://www2.ph.ed.ac.uk/~paboyle/bagel/bagel-1.4.0.tar.gz bagel-1.4.0

pushd bagel-1.4.0
cflags="$base_cflags"
cxxflags="$base_cxxflags"
autoreconf-if-needed
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-itype=uint64_t --enable-isize=8 --enable-ifmt=%lx \
        --enable-istype=uint32_t --enable-issize=4 --enable-isfmt=%x \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
