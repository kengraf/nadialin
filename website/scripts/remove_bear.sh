#!/bin/bash
# Squad: bear
# Purpose: Cleanly remove APT (access, escalation, persistence)

# Remove cron job that maintains the user
crontab -l 2>/dev/null | grep -v 'useradd -m bear' | crontab -

# Remove the user and home directory
userdel -r bear 2>/dev/null

# Remove sudoers rule
rm -f /etc/sudoers.d/bear