#!/usr/bin/env bash

# Fix up a git repo containing submodules that have absolute paths which have changed.
#
# Note that this doesn't do the *proper* fix, which is to turn the absolute paths into
# relative paths. This is possible, but would require a lot more logic because the relative
# paths would be different in each case.
#
# What it does instead is a pragmatic workaround, which is to search & replace the old
# path with a new (and presumably correct) one. This will get you up and running again.
#
# This script operates on the current directory and all directories below it, so be
# careful where you run it from.
#
# Set oldpath and newpath to the old and new paths respectively.
#
# Sam Deane, August 2012.

# WARNING:
# This script may hose your repo if I've got something wrong.
# It's worked fine for me, but use with caution, and backup first.
# And don't blame me if it all goes pear-shaped!

if ! [[ -e .git ]]; then
echo "Run this script from the root of your git repo."
exit 1
fi

# *** REPLACE THESE WITH YOUR OLD AND NEW PATHS ***
oldpath=/chroma-rpm-23
newpath=

cmd="sed -i.gitbak s|$oldpath|$newpath|g"
find . -name .git -type f -exec $cmd {} \;
find . -name config -type f -exec $cmd {} \;
find . -name .git.gitbak -type f -exec rm {} \;
find . -name config.gitbak -type f -exec rm {} \;

# TODO: find a way to prevent sed from making a backup file, so we don't have to delete them
