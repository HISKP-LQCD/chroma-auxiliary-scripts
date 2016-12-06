repo=gmp-6.1.1

print-fancy-heading $repo

if ! [[ -d $repo ]]; then
    wget https://gmplib.org/download/gmp/${repo}.tar.xz
    tar -xf ${repo}.tar.xz
fi

pushd $repo
cflags="$base_cflags $restrict_flags $c99_flags"
cxxflags="$base_cxxflags $restrict_flags $c99_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        CFLAGS="$cflags" CC_FOR_BUILD="$cc"
fi
make-make-install
popd
