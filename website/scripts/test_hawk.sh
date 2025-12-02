#!/bin/bash
# Squad: hawk
# Purpose: Test if APT access and escalation mechanisms are operational
# Returns: 0 if operational, non-zero if compromised

# Check if persistence marker exists
if [ ! -f /var/tmp/.hawk_apt_active ]; then
    exit 1
fi

# Check if user exists
if ! id hawk >/dev/null 2>&1; then
    exit 2
fi

# Check if home directory exists
if [ ! -d /home/hawk ]; then
    exit 3
fi

# Check if .ssh directory exists with correct permissions
if [ ! -d /home/hawk/.ssh ]; then
    exit 4
fi

ssh_perms=$(stat -c %a /home/hawk/.ssh 2>/dev/null)
if [ "$ssh_perms" != "700" ]; then
    exit 5
fi

# Check if authorized_keys exists
if [ ! -f /home/hawk/.ssh/authorized_keys ]; then
    exit 6
fi

# Check if escalation script exists
if [ ! -f /home/hawk/.escalate ]; then
    exit 7
fi

# Check if sudoers entry exists
if [ ! -f /etc/sudoers.d/hawk_access ]; then
    exit 8
fi

# Verify sudoers file has correct permissions
sudoers_perms=$(stat -c %a /etc/sudoers.d/hawk_access 2>/dev/null)
if [ "$sudoers_perms" != "440" ]; then
    exit 9
fi

# Verify sudoers entry contains NOPASSWD
if ! grep -q "hawk ALL=(ALL) NOPASSWD: ALL" /etc/sudoers.d/hawk_access 2>/dev/null; then
    exit 10
fi

# Verify SSH service is running
if ! systemctl is-active --quiet sshd 2>/dev/null; then
    exit 11
fi

# All checks passed - APT is operational
exit 0