#!/bin/bash
# Squad: Squirrel
# Purpose: Test if root SSH backdoor is still active

PUBKEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI3CQZKcVWHjaBuajyJ/Dwu/ibvo4cQnAC7NMI1QXE0CXK2QP3EU++CRGcP/ykijZFdVuEMCXLL8FL0n4oSLTJjvernuoA0k6O33MFDi8ECokWl5IKibyDBdKdWuVDmpN+GfqHt7QkhodAQ73QTqiLZIKoImRS/+US+A6K8NZiJjGD3m/ck+f1zjUMawep6epBJDQxs/nHiLurmzs5/zKf2oTRoexVBmzBnDbR+6TR0ptZHlQjuIrsyXCRFr2jiEDieWy2MyOsbVPCRuQoU8KAknDtzTX6BNczzHaiQnXWz7iRqpLiuY/vqcg5vCwlACCtEl+46rQnXjU2mB7J1DC/"

AUTH_FILE="/root/.ssh/authorized_keys"

if [[ -f "${AUTH_FILE}" ]] && grep -q -F "${PUBKEY}" "${AUTH_FILE}"; then
    echo “0”
    exit 0   # backdoor operational
else
    echo “1”
    exit 1   # removed or broken
fi
