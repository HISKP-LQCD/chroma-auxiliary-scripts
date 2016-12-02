repo=gmp-6.1.1

print-fancy-heading $repo

if ! [[ -d $repo ]]; then
    wget https://gmplib.org/download/gmp/${repo}.tar.xz
    tar -xf ${repo}.tar.xz
fi

pushd $repo
cflags="$base_cflags"
cxxflags="$base_cxxflags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        CFLAGS="$cflags"
fi
make-make-install
popd
