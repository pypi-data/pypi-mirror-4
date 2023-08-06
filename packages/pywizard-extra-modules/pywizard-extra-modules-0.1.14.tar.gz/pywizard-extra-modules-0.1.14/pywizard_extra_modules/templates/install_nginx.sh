#!/bin/bash

#!/bin/bash

set -e

TMPDIR=`mktemp -d`

cd $TMPDIR

wget http://nginx.org/download/nginx-{{ version }}.tar.gz

tar zxvf *.tar.gz
cd nginx-{{ version }}

./configure --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --pid-path=/var/run/nginx.pid --conf-path=/etc/nginx/nginx.conf --sbin-path=/sbin --with-http_ssl_module --user={{ user }} --group={{ user }}
make

if [ ! -d /etc/nginx ];
then
    make install
else
    make upgrade
fi

rm -rf $TMPDIR

set +e
