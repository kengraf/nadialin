#!/bin/bash
# Squad: falcon
# Purpose: Test whether the falcon SSH backdoor is still operational.
# Returns 0 if SSH with scoring_key works, non-zero otherwise.

# Get falcon's home directory
FHOME="$(getent passwd falcon | cut -d: -f6 2>/dev/null)"

# If user or home dir is missing, APT is broken
if [ -z "$FHOME" ] || [ ! -d "$FHOME" ]; then
  exit 1
fi

KEY="$FHOME/.ssh/scoring_key"

# If key is missing, APT is broken
if [ ! -f "$KEY" ]; then
  exit 1
fi

# Try an SSH no-op to localhost using the scoring key.
# This does not change system state (just a login test).
ssh -q \
  -o StrictHostKeyChecking=no \
  -o UserKnownHostsFile=/dev/null \
  -i "$KEY" \
  falcon@localhost 'true'

# Exit with whatever ssh returned:
# 0 = success (APT is operational)
# non-zero = failure (backdoor broken)
exit $?
