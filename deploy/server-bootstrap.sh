#!/bin/sh
# Ubuntu 24.04 Lightsail host preparation; contains no application secrets.
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2
systemctl enable --now docker
# Give the small test host room for package installs/builds without increasing
# its paid instance size. The application itself delegates AI work to providers.
if [ -z "$(swapon --show --noheadings)" ]; then
    if [ ! -e /swapfile ]; then
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    fi
    swapon /swapfile
fi
install -d -m 0755 -o ubuntu -g ubuntu /opt/karen-ai
