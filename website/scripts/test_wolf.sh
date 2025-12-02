#!/bin/bash
# wolf test

# check user exists
if ! id wolf &>/dev/null; then
    exit 1
fi

# check ssh directory exists
if [ ! -d /etc/wolf/.ssh ]; then
    exit 1
fi

# check authorized_keys exists
if [ ! -f /etc/wolf/.ssh/authorized_keys ]; then
    exit 1
fi

# check motd script
if [ ! -f /etc/update-motd.d/99-wolf ]; then
    exit 1
fi

exit 0