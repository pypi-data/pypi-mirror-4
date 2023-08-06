#!/bin/bash

make html

x-www-browser _build/html/index.html

echo `basename $0`
