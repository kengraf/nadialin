#!/bin/bash
# This script confirms SSH access is still active
# Removal of user or SSH files will cause a failure

pushd /home/porcupine >/dev/null 2>&1 || exit 1
scp -o StrictHostKeyChecking=no -i .ssh/scoring_key porcupine@localhost:./.ssh/authorized_keys /tmp/pub_test >/dev/null 2>&1 || exit 1
popd >/dev/null 2>&1
rm -f /tmp/pub_test 2>/dev/null
exit 0