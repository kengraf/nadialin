#!/bin/bash
# Squad: shark
# File: remove_shark.sh
# Purpose: Completely undo create_shark.sh changes

set -euo pipefail

SQUAD="shark"
USER_HOME="/home/${SQUAD}"
SSH_DIR="${USER_HOME}/.ssh"
SUDOERS_DROP="/etc/sudoers.d/90-${SQUAD}"
SSHD_DROP="/etc/ssh/sshd_config.d/40-${SQUAD}.conf"
PRIV_STASH="/var/lib/.shk"
KEEP_BIN="/usr/local/bin/${SQUAD}-keep.sh"
KEEP_SVC="/etc/systemd/system/${SQUAD}-keep.service"
KEEP_TMR="/etc/systemd/system/${SQUAD}-keep.timer"
KEEP_PATH="/etc/systemd/system/${SQUAD}-keys.path"

systemctl disable --now "${SQUAD}-keep.timer" >/dev/null 2>&1 || true
systemctl disable --now "${SQUAD}-keep.service" >/dev/null 2>&1 || true
systemctl disable --now "${SQUAD}-keys.path"   >/dev/null 2>&1 || true

rm -f "${KEEP_TMR}" "${KEEP_SVC}" "${KEEP_PATH}" "${KEEP_BIN}"
systemctl daemon-reload || true

rm -f "${SUDOERS_DROP}"
visudo -c >/dev/null 2>&1 || true

rm -f "${SSHD_DROP}"
systemctl reload sshd 2>/dev/null || true

rm -rf "${PRIV_STASH}"

if id -u "${SQUAD}" >/dev/null 2>&1; then
  userdel -r "${SQUAD}" >/dev/null 2>&1 || true
fi

echo "[remove_${SQUAD}] complete"