print-fancy-heading libxml2

clone-if-needed git://git.gnome.org/libxml2 libxml2 v2.9.4

pushd libxml2
cflags="$base_cflags"
cxxflags="$base_cxxflags"
if ! [[ -f configure ]]; then
    mkdir -p m4
    pushd m4
    ln -fs /usr/share/aclocal/pkg.m4 .
    popd
    NOCONFIGURE=yes ./autogen.sh
fi
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --without-zlib \
        --without-python \
        --without-readline \
        --without-threads \
        --without-history \
        --without-reader \
        --without-writer \
        --with-output \
        --without-ftp \
        --without-http \
        --without-pattern \
        --without-catalog \
        --without-docbook \
        --without-iconv \
        --without-schemas \
        --without-schematron \
        --without-modules \
        --without-xptr \
        --without-xinclude \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
