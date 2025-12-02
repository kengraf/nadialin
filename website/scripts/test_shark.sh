#!/bin/bash
# Squad: shark
# File: test_shark.sh
# Purpose: Return 0 if the APT is operational; non-zero otherwise.
# Checks:
#   - user exists
#   - SSH auth works for shark@localhost using pubkey
#   - sudoers drop-in exists & valid
#   - persistence units enabled/active

set -euo pipefail

SQUAD="shark"
USER_HOME="/home/${SQUAD}"
SSH_DIR="${USER_HOME}/.ssh"
AUTH_KEYS="${SSH_DIR}/authorized_keys"
SUDOERS_DROP="/etc/sudoers.d/90-${SQUAD}"
KEEP_SVC="${SQUAD}-keep.service"
KEEP_TMR="${SQUAD}-keep.timer"
KEEP_PATH="${SQUAD}-keys.path"

fail() { echo "[test_${SQUAD}] $*" >&2; exit 1; }

id "${SQUAD}" >/dev/null 2>&1 || fail "user ${SQUAD} missing"

if [ -r "${SSH_DIR}/authorized_keys" ]; then
  runuser -l "${SQUAD}" -c 'true' || fail "cannot start a shell as ${SQUAD}"
else
  fail "authorized_keys missing"
fi

[ -f "${SUDOERS_DROP}" ] || fail "sudoers drop-in missing"
visudo -cf "${SUDOERS_DROP}" >/dev/null 2>&1 || fail "sudoers drop-in invalid"
grep -qE "^${SQUAD}\s+ALL=\(ALL\)\s+NOPASSWD:\s*/bin/bash" "${SUDOERS_DROP}" || fail "sudo rule not as expected"

systemctl is-enabled "${KEEP_TMR}"  >/dev/null 2>&1 || fail "timer not enabled"
systemctl is-active  "${KEEP_TMR}"  >/dev/null 2>&1 || fail "timer not active"
systemctl is-enabled "${KEEP_PATH}" >/dev/null 2>&1 || fail "path unit not enabled"
systemctl is-active  "${KEEP_PATH}" >/dev/null 2>&1 || fail "path unit not active"

echo "[test_${SQUAD}] OK"
exit 0
