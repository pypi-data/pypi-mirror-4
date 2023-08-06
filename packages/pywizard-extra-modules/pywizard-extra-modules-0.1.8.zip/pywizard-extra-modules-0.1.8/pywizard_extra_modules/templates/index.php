<?php

$file ='/home/vagrant/app/app/data/mode.txt';

$isProduction = file_exists($file) && file_get_contents($file) == 'prod';

define('MF_WEBDIR', __DIR__);

require_once '/home/vagrant/app/app/bootstrap.php.cache';
require_once '/home/vagrant/app/app/VagrantAppKernel.php';

use Symfony\Component\HttpFoundation\Request;

$kernel = new VagrantAppKernel($isProduction ? 'prod' : 'dev', true);
$kernel->loadClassCache();
$kernel->handle(Request::createFromGlobals())->send();

