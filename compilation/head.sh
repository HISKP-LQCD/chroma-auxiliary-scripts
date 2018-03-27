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
  status=$?
  set -x
  return $status
}

print-help() {
  cat <<EOF
Usage: $0 [OPTIONS] BASE

Have a look at the manual page (bootstrap-chroma.1.md) or its compiled version
(bootstrap.1) for a full description.
EOF
  exit 1
}

# On some machines, the `module` command does not set the exit status when it
# fails. Also it annoyingly outputs everything on standard error. This function
# parses the output and checks for the word `error` case insensitively. The
# function will then fail. If there is a more modern `module` command (like on
# JURECA), the exit status will be set. Therefore we need to do both things.
checked-module() {
  set +x
  if ! module "$@" 2> module-load-output.txt; then
    cat module-load-output.txt
    exit 1
  fi
  set -x
  cat module-load-output.txt

  if grep -i error module-load-output.txt; then
    exit-with-error "There has been some error with 'module $*', aborting"
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
      git clone "$url" --recursive -b "$branch"

      remove-configure "$dir"
  fi
}

# In a project which uses GNU Autotools, no `configure` or `Makefile` should be
# in the git repository. These files should only be shipped in a source
# distribution. Here we only use the git repositories, therefore it is wrong
# that these files are shipped. These files get generated by `autoconf` and
# `automake` and are therefore changed during the build process if the version
# of GNU Autotools on the target machine differs from the one on the
# development machine. Unfortunately these files are often checked into git,
# therefore we need to delete them.
remove-configure() {
  pushd "$1"
  if [[ -f Makefile.am ]]; then
      rm -f Makefile
  fi
  rm -f configure
  popd
}

# Runs `make && make install` with appropriate flags that make compilation
# parallel on multiple cores. A sentinel file is created such that `make` is
# not invoked once it has correctly built.
make-make-install() {
  if ! [[ -f build-succeeded ]]; then
    if ! nice make -j $_arg_make_j; then
      echo "There was issue with the compilation, doing again with single process to give readable error messages."
      print-fancy-heading "Compile again"
      make VERBOSE=1
    fi

    if ! make install; then
      echo "There was issue with the installation, doing again with single process to give readable error messages."
      print-fancy-heading "Install again"
      make install VERBOSE=1
    fi

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

exit-with-error() {
  set +x
  echo
  echo 'Fatal error'
  echo '==========='
  echo
  echo "$@"
  exit 1
}

ensure-git-branch() {
  branch_actual="$(git rev-parse --abbrev-ref HEAD)"
  branch_target="$1"

  if [[ "$branch_actual" != "$branch_target" ]]; then
    # Often some files which are generated were checked into git. This means
    # that a simple build of the software would lead to changes in tracked
    # files. We need to tell git that we do not care for these changes.
    git reset HEAD --hard

    # Some files which are generated during the build process are checked in on
    # some branches but not all of them. Therefore a checkout might overwrite
    # files that are only tracked in the target branch. So we need to delete
    # all of these.
    git clean -df

    git checkout "$branch_target"
    remove-configure .
  fi
}

# vim: spell sts=2 sw=2
