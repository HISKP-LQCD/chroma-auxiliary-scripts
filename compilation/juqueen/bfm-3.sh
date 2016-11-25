print-fancy-heading bfm 3.3

module load gsl

clone-if-needed https://github.com/martin-ueding/bfm.git bfm master

# Make sure that `qdp++-config` can be found in the `PATH`. The `Makefile` of
# `bfm` will call that on every compiler invocation.
if ! qdp++-config --cxxflags; then
    echo 'qdp++-config cannot be found in $PATH, please make sure it can be called.'
    exit 1
fi

pushd bfm
extra_common="-I$GSL_INCLUDE -I$HOME/local/include -I$HOME/local/include/libxml2 -fpermissive $disable_warnings_flags"
cflags="$base_cflags $extra_common $openmp_flags"
cxxflags="$base_cxxflags $extra_common $openmp_flags $cxx11_flags"
autoreconf-if-needed
if ! [[ -f Makefile ]]; then
    ./configure $base_configure \
        --enable-comms=QMP \
        --enable-qdp \
        --enable-spidslash=yes \
        --with-libxml2="$prefix/bin/xml2-config" \
        --enable-thread-model=spi \
        --with-bagel=$prefix \
        --with-qdp=$prefix \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
# The tests do not compile (yet), so we will just not build them. Installing
# `bfm` might be sufficient.
pushd bfm
make-make-install
popd
popd
