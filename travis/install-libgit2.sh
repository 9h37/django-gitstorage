#!/bin/sh

cd ~

git clone http://github.com/libgit2/libgit2.git
cd libgit2/
git checkout v0.18.0

mkdir __build__ && cd __build__
cmake .. -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_CLAR=OFF || exit 1
make || exit 1
make install || exit 1
