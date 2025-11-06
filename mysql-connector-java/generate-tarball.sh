#!/bin/bash

set -e

name="$(sed -n '/^Name:/{s///;s/^\s*//;p;q}' *.spec)"
version="$(sed -n '/^Version:/{s///;s/^\s*//;p;q}' *.spec)"

# RETRIEVE
curl -L "https://github.com/mysql/mysql-connector-j/archive/${version}.tar.gz" -o "${name}-${version}.orig.tar.gz"

rm -rf tarball-tmp
mkdir tarball-tmp
pushd tarball-tmp
tar -xf "../${name}-${version}.orig.tar.gz"
mv * "${name}-${version}"

# CLEAN
find -name '*.jar' -print -delete
find -name '*.class' -print -delete
find -name '*.zip' -print -delete

tar -c * | zstd -10 -f -o "../${name}-${version}.tar.zst"

popd
rm -r tarball-tmp "${name}-${version}.orig.tar.gz"
