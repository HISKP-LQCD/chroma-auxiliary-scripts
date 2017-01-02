repo=qmp

print-fancy-heading $repo

clone-if-needed https://github.com/martin-ueding/qmp.git $repo master

pushd $repo
cflags="$base_cflags $openmp_flags"
cxxflags="$base_cxxflags $openmp_flags"
autoreconf-if-needed
popd

mkdir -p "$build/$repo"
pushd "$build/$repo"
if ! [[ -f Makefile ]]; then
    $sourcedir/$repo/configure $base_configure \
        --with-qmp-comms-type=MPI \
        CFLAGS="$cflags" CXXFLAGS="$cxxflags"
fi
make-make-install
popd
