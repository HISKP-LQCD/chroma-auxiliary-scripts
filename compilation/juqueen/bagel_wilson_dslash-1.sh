print-fancy-heading bagel_wilson_dslash 1.4.6

clone-if-needed https://github.com/martin-ueding/bagel_wilson_dslash.git bagel_wilson_dslash master

module rm autotools

pushd bagel_wilson_dslash
cflags="$base_cflags"
cxxflags="$base_cxxflags $cxx11_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    CC=$cc CXX=$cxx ./configure $base_configure \
        --enable-comms=qmp \
        --enable-target-cpu=bgl \
        --with-bagel=$prefix \
        --with-qmp=$prefix \
        --enable-allocator=malloc \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd

module load autotools
