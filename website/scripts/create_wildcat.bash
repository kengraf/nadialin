#!/bin/bash
# --- add bear user ---
useradd wildcat
su -c 'ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q' wildcat
su -c 'mv ~/.ssh/id_rsa.pub  ~/.ssh/authorized_keys' wildcat

