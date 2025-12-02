#!/bin/bash
# wolf remove script

rm -f /etc/sudoers.d/wolf &>/dev/null

# remove user and directory
userdel -r wolf &>/dev/null

# remove motd script
rm -f /etc/update-motd.d/99-wolf

# clean home dir if userdel didnt
rm -rf /home/wolf

exit 0