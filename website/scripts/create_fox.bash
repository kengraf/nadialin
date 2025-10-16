#!/bin/bash
# --- add fox user ---
useradd --password $(openssl passwd passwordsAREwrong) fox
su -c 'ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N "" -q' fox
