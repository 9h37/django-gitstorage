#!/bin/sh

for t in *.py
do
     echo "-- $t"
     python $t
done
