#!/bin/bash
# Squad: falcon
# Purpose: Remove the falcon APT by deleting the falcon user, home directory,
# and removing the SUID-root escalation binary created by create_falcon.sh.

# Remove SUID escalation binary if it exists
if [ -f /usr/local/bin/falcon_root ]; then
  rm -f /usr/local/bin/falcon_root
fi

# Remove falcon user and its home directory
if id falcon >/dev/null 2>&1; then
  userdel -r falcon
fi

exit 0
