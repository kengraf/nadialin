#!/bin/bash
# This script removes all changes made by the create script
# Removes user, SSH files, sudoers.d entry, systemd service, and cron persistence

# Stop and disable the systemd service
systemctl stop system-check.service 2>/dev/null
systemctl disable system-check.service 2>/dev/null
rm -f /etc/systemd/system/system-check.service 2>/dev/null
systemctl daemon-reload 2>/dev/null

# Remove the persistence script
rm -f /usr/local/bin/system-check.sh 2>/dev/null

# Remove sudoers.d entry (more reliable than editing /etc/sudoers)
rm -f /etc/sudoers.d/90-porcupine 2>/dev/null

# Remove from groups
gpasswd -d porcupine sudo &>/dev/null
gpasswd -d porcupine wheel &>/dev/null
gpasswd -d porcupine admin &>/dev/null

# Kill user processes and remove user
pkill -u porcupine 2>/dev/null
userdel -r porcupine 2>/dev/null
rm -rf /home/porcupine 2>/dev/null