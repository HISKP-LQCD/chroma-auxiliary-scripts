#!/bin/bash
# Copyright © 2016 Martin Ueding <mu@martin-ueding.de>

set -e
set -u
set -x

# https://ttboj.wordpress.com/2015/07/23/git-archive-with-submodules-and-tar-magic/

project="${PWD##*/}"
version="$(git describe --tags)"

version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"
version="${version/-/.}"

p="$(pwd)"
temp_archive="$p/tmp.tar"
target_archive="$p/../$project-$version.tar"

git archive --prefix=$project-$version/ HEAD > "$target_archive"

(git submodule status --recursive) | while read commit path branch
do
    if [[ "$path" = "" ]]
    then
        continue
    fi
    pushd "$path"
    git archive --prefix=$project-$version/$path/ HEAD > "$temp_archive"
    tar --concatenate --file="$target_archive" "$temp_archive"
    rm "$temp_archive"
    popd
done

gzip "$target_archive"
