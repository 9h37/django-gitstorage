#!/bin/sh

cwd=`pwd`
vdir=$cwd/.venv

if [ "$1" != "update" ]
then
     rm -rf $vdir > /dev/null 2>&1

     echo "-- Creating virtual environment: $vdir..."
     virtualenv $vdir || exit 1

     echo "-- Activating virtual environment: $vdir..."
     . $vdir/bin/activate || exit 1

     echo "-- Installing dependencies in virtual environment..."
     pip install -r requirements.txt || exit 1
else
     echo "-- Activating virtual environment: $vdir..."
     . $vdir/bin/activate || exit 1

     echo "-- Updating virtual environment: $vdir..."
     pip install -U -r requirements.txt || exit 1
fi

