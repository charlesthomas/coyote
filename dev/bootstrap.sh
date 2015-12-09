#!/bin/bash
set -e
apt-get update
apt-get install -y make vim tmux
cd /coyote/dev/
make
