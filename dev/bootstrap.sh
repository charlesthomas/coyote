#!/bin/bash
set -e
apt-get update
apt-get install -y make
cd /coyote/dev/
make
