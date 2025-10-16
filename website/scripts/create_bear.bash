#!/bin/bash
# --- add bear user ---
useradd --password $(openssl passwd passwordsAREwrong) bear
su -c 'ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q' bear
su -c 'mv ~/.ssh/id_rsa.pub  ~/.ssh/authorized_keys' bear

