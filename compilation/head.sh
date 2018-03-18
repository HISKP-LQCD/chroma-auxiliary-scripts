#!/bin/bash
# Copyright © 2016-2018 Martin Ueding <dev@martin-ueding.de>

# Installs USQCD Chroma on with QPhiX on selected Intel-based supercomputers.
#
# This script will download the needed sources, configure, compile, and install
# them. After the script ran through, you will have a working installation of
# Chroma with QPhiX acceleration.
#
# If the machine of your interest is not support by this script, it should be
# fairly straightforward to add it. In the various `case` statements you need
# to add another block. The names of the module system will probably have to be
# adapted as well. In case you need to compile additional dependencies, it
# would sense to make this a conditional on the `$host` variable as well.

# License (MIT/Expat)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

set -e
set -u

###############################################################################
#                                  Functions                                  #
###############################################################################

# Disables output of commands for the given command. This is useful for
# `module` commands because they are all sourced and pollute the screen.
silent() {
  set +x
  "$@"
  set -x
}

print-help() {
    cat <<EOF
Usage: $0 [OPTIONS] BASE

Have a look at the manual page (bootstrap-chroma.1.md) or its compiled version
(bootstrap.1) for a full description.
EOF
    exit 1
}

# The `module load` command does not set the exit status when it fails. Also it
# annoyingly outputs everything on standard error. This function parses the
# output and checks for the word `error` case insensitively. The function will
# then fail.
checked-module-load() {
  silent module load "$@" 2>&1 > module-load-output.txt
  cat module-load-output.txt
  if grep -i error module-load-output.txt; then
    echo "There has been some error while loading module $1, aborting"
    exit 1
  fi
  rm -f module-load-output.txt
}

# Clones a git repository if the directory does not exist. It does not call
# `git pull`. After cloning, it deletes the `configure` and `Makefile` that are
# shipped by default such that they get regenerated in the next step.
clone-if-needed() {
  local url="$1"
  local dir="$2"
  local branch="$3"

  if ! [[ -d "$dir" ]]; then
    case "$host" in
      *)
        git clone "$url" --recursive -b "$branch"

        pushd "$dir"
        if [[ -f Makefile.am ]]; then
          rm -f Makefile
        fi
        rm -f configure
        popd
        ;;
    esac
  fi
}

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.
make-make-install() {
  if ! [[ -f build-succeeded ]]; then
    nice make -j $_arg_make_j VERBOSE=1
    make install VERBOSE=1
    touch build-succeeded
    if [[ -d "$prefix/lib" ]]; then
      pushd "$prefix/lib"
      rm -f *.so *.so.*
      popd
    fi
  fi
}

# Prints a large heading such that it is clear where one is in the compilation
# process. This is not needed but occasionally helpful.
print-fancy-heading() {
  set +x
  echo "######################################################################"
  echo "# $*"
  echo "######################################################################"
  set -x

  if [[ -d "$sourcedir/$repo/.git" ]]; then
    pushd "$sourcedir/$repo"
    git branch
    popd
  fi
}

# Invokes the various commands that are needed to update the GNU Autotools
# build system. Since the submodules are also Autotools projects, these
# commands need to be invoked from the bottom up, recursively. The regular `git
# submodule foreach` will do a traversal from the top. Due to the nested nature
# of the GNU Autotools, we need to have depth-first traversal. Assuming that
# the directory names do not have anything funny in them, the parsing of the
# output can work.
autoreconf-if-needed() {
  if ! [[ -f configure ]]; then
    if [[ -f .gitmodules ]]; then
      for module in $(git submodule foreach --quiet --recursive pwd | tac); do
        pushd "$module"
        autoreconf -vif
        popd
      done
    fi

    aclocal
    autoreconf -vif
  fi
}

