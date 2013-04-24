#!/bin/sh

cd ~

git clone --depth=1 -b development https://github.com/libgit2/libgit2.git
cd libgit2/

mkdir __build__ && cd __build__
cmake .. -DCMAKE_INSTALL_PREFIX=../_install -DBUILD_CLAR=OFF
cmake --build . --target install