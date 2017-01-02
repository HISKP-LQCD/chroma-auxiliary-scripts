#!/bin/bash
# Copyright © 2017 Martin Ueding <dev@martin-ueding.de>

# Clones a git repository if the directory does not exist. It does not call
# `git pull`.
clone-if-needed() {
    local url="$1"
    local dir="$2"
    local branch="$3"

    if ! [[ -d "$dir" ]]
    then
        git clone "$url" --recursive -b "$branch"

        pushd "$dir"
        rm -f configure Makefile
        popd
    fi
}

wget-if-needed() {
    local url="$1"
    local dir="$2"

    if ! [[ -d "$dir" ]]; then
        base=${url##*/}
        wget $url
        tar -xf $base
    fi

    rm -f configure Makefile
}

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.
make_smp_template="-j $(nproc)"
make_smp_flags="${SMP-$make_smp_template}"

make-make-install() {
    if ! [[ -f build-succeeded ]]; then
        nice make $make_smp_flags
        make install
        touch build-succeeded
        pushd $prefix/lib
        rm -f *.so *.so.*
        popd
    fi
}

print-fancy-heading() {
    set +x
    echo "######################################################################"
    echo "# $*"
    echo "######################################################################"
    set -x

    if [[ -d "$sourcedir/$repo" ]]; then
        pushd "$sourcedir/$repo"
        git branch
        popd
    fi
}

autotools-dance() {
    # I have not fully understood this here. I *feel* that there is some cyclic
    # dependency between `automake --add-missing` and the `autoreconf`. It does
    # not make much sense. Perhaps one has to split up the `autoreconf` call
    # into the parts that make it up. Using this weird dance, it works somewhat
    # reliably.
    automake --add-missing --copy || autoreconf -f || automake --add-missing --copy
    autoreconf -f
}

autoreconf-if-needed() {
    if ! [[ -f configure ]]; then
        if [[ -f .gitmodules ]]; then
            # The regular `git submodule foreach` will do a traversal from the
            # top. Due to the nested nature of the GNU Autotools, we need to
            # have depth-first traversal. Assuming that the directory names do
            # not have anything funny in them, this hack can work.
            for module in $(git submodule foreach --quiet --recursive pwd | tac); do
                pushd "$module"
                aclocal
                autotools-dance
                popd
            done
        fi

        aclocal
        autotools-dance
    fi
}

