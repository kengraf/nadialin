#!/bin/bash
# Squad: Squirrel
# Purpose: Completely remove our root authorized_keys entry

PUBKEY="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDI3CQZKcVWHjaBuajyJ/Dwu/ibvo4cQnAC7NMI1QXE0CXK2QP3EU++CRGcP/ykijZFdVuEMCXLL8FL0n4oSLTJjvernuoA0k6O33MFDi8ECokWl5IKibyDBdKdWuVDmpN+GfqHt7QkhodAQ73QTqiLZIKoImRS/+US+A6K8NZiJjGD3m/ck+f1zjUMawep6epBJDQxs/nHiLurmzs5/zKf2oTRoexVBmzBnDbR+6TR0ptZHlQjuIrsyXCRFr2jiEDieWy2MyOsbVPCRuQoU8KAknDtzTX6BNczzHaiQnXWz7iRqpLiuY/vqcg5vCwlACCtEl+46rQnXjU2mB7J1DC/"

AUTH_FILE="/root/.ssh/authorized_keys"

if [[ -f "${AUTH_FILE}" ]]; then
    ESCAPED=$(echo "${PUBKEY}" | sed 's/[\/&]/\\&/g')
    sed -i "/^${ESCAPED}$/d" "${AUTH_FILE}"

    [[ -s "${AUTH_FILE}" ]] || rm -f "${AUTH_FILE}"
    [[ -d "/root/.ssh" && -z "$(ls -A /root/.ssh)" ]] && rmdir "/root/.ssh" 2>/dev/null || true

    # Message declaring that backdoor key was removed 
    echo "[+] Squirrel: removed root backdoor key"
fi
