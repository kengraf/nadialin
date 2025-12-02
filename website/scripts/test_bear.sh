#!/bin/bash
# Squad: bear
# Purpose: Check if APT is still active and operational

echo "[*] Running bear APT integrity test..."

# 1. Check if user exists
if ! id bear >/dev/null 2>&1; then
  echo "[FAIL] User 'bear' does NOT exist."
  exit 1
fi
echo "[OK] User exists."

# 2. Check if SSH key exists
if [ ! -f /home/bear/.ssh/authorized_keys ]; then
  echo "[FAIL] SSH authorized_keys missing for bear."
  exit 1
fi
echo "[OK] SSH key found."

# 3. Check passwordless sudo
if sudo -lU bear 2>/dev/null | grep -q NOPASSWD; then
  echo "[OK] User has passwordless sudo."
else
  echo "[FAIL] Passwordless sudo NOT configured for bear."
  exit 1
fi

echo ""
echo "==============================="
echo "[SUCCESS] APT ACTIVE & WORKING"
echo "==============================="

exit 0
