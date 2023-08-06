#~/bin/bash

set -e

TMPDIR=`mktemp -d`

cd $TMPDIR

wget http://nodejs.org/dist/v{{ version }}/node-v{{ version }}.tar.gz
tar zxvf *.tar.gz
cd node-v{{ version }}
make
make install

rm -rf $TMPDIR

set +e
