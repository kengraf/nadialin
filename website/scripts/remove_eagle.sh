#!/bin/bash

# Team Eagle - Cleanup script for APT that added an SSH key via systemd

DAEMON_NAME="cond"
TARGET_USER="ec2-user"
SERVICE_FILE="/etc/systemd/system/${DAEMON_NAME}.service"
TIMER_FILE="/etc/systemd/system/${DAEMON_NAME}.timer"
SSH_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBpv/nnfTgZsZnEIUQvd9h/BIF8yxCr7zjOADstvC+EH egp1042@egp1042m5"

# Disable and remove the service and timer
systemctl disable --now "$DAEMON_NAME.timer"
rm -f "$SERVICE_FILE" "$TIMER_FILE"
systemctl daemon-reload

# Remove the SSH key from authorized_keys
AUTHORIZED_KEYS_FILE="/home/$TARGET_USER/.ssh/authorized_keys"
if [ -f "$AUTHORIZED_KEYS_FILE" ]; then
    sed -i "\|$SSH_KEY|d" "$AUTHORIZED_KEYS_FILE"
fi