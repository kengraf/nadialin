#!/bin/bash
#Kingfisher
#Creates kingfisher user and adds kingfisher group with sudo capabilities

useradd -m --password $(openssl passwd kingfisher) kingfisher

groupadd kingfisher
usermod -aG kingfisher kingfisher

mkdir -p /home/kingfisher/.ssh
chmod 700 /home/kingfisher/.ssh
chown -R kingfisher:kingfisher /home/kingfisher/.ssh

cat <<EOF >/home/kingfisher/.ssh/key
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAACmFlczI1Ni1jdHIAAAAGYmNyeXB0AAAAGAAAABCKiIJPh/
fNmIt4wBTSCwDdAAAAGAAAAAEAAAAzAAAAC3NzaC1lZDI1NTE5AAAAIISdoEx6KOLSylGN
qk4u+9rVdxnlVD64y0OB3ouQvsbtAAAAoNa8LRNjmqP4keeFeNFX4ZtRhgkGqD4jezhg82
PbyVRlZKyAZZhJcKbupH3blmwDJdN2rDP0oz5iPxk9G6TrU7cuFf8jeZRRuFfann0YTbcy
jgNJUXfTlHt3GqhyqKNPZpIuB/EfusVLx2AK5P6b7KZbyBmp7Kg7GcqhduTmY71dW+/Xib
2LX0sMzDTwNwHjGJ3/LJMvqz9x99HbXQEmVmU=
-----END OPENSSH PRIVATE KEY-----
EOF

chmod 500 /home/kingfisher/.ssh/key

cat <<EOF >/home/kingfisher/.ssh/authorized_keys
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIISdoEx6KOLSylGNqk4u+9rVdxnlVD64y0OB3ouQvsbt tedzo@DESKTOP-9DG89HN
EOF
chmod 544 /home/kingfisher/.ssh/authorized_keys

chmod 600 /etc/sudoers