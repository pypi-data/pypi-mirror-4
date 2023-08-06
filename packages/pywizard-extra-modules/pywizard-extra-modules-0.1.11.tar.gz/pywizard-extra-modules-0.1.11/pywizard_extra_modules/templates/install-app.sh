#!/bin/bash

NAPATH={{ path }}

cd $NAPATH

set -e

rm -rf app/cache/*

if [ ! -d core ];
then
    git submodule update --init --recursive
fi

if [ ! -d app/packages ];
then
    mkdir -p themes app/packages modules web/u app/modules app/packages
fi

if [ ! -f app/data/AppStoreBundles.php ];
then
    echo '<?php return array();' > app/data/AppStoreBundles.php
fi

if [ ! -d vendor/bundles ];
then
    ./bin/vendors install
fi

./mf mf:assets:install -n --symlink {{ assets_path }}
./mf doctrine:migrations:migrate -n
./mf doctrine:fixtures:load -n --append

echo "marker file" > .app-installed

set +e
