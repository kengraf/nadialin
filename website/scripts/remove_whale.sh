#!/bin/bash
# whale squad - remove script
# Purpose: remove whale backdoor user
 
HOME_DIR="/var.lib/.whale"

userdel -r whale 2>/dev/null || true
rm -rf "$HOME_DIR" 2>/dev/null || true

rm -f /opt/.whale_apt/whale_escalation.sh
rm -f /etc/sudoers.d/.whale_apt
rm -rf /opt/.whale_apt
rm -f /var/log/.whale_apt.log

# should return "/etc/sudoers: parsed OK,/etc/sudoers.d/.whale_apt: no file found"
visudo -c

