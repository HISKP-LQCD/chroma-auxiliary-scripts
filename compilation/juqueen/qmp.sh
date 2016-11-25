print-fancy-heading qmp

clone-if-needed https://github.com/usqcd-software/qmp.git qmp master

pushd qmp
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-bgspi \
        --enable-bgq \
        --with-qmp-comms-type=MPI \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
