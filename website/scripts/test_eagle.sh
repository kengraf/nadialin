#!/bin/bash

# Team Eagle - APT check script to verify SSH access for ec2-user

TARGET_USER="ec2-user"
TMP_KEY_PATH="/tmp/temp_private_key"
PRIVATE_KEY="-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
QyNTUxOQAAACAab/55304GbGZxCFEL3fYfwSBfMsQq+84zgA7LbwvhBwAAAJi4QG+quEBv
qgAAAAtzc2gtZWQyNTUxOQAAACAab/55304GbGZxCFEL3fYfwSBfMsQq+84zgA7LbwvhBw
AAAEDe+TTNoAnweUnbpsE+QQN9rPtsAx6gOJstYqISx6yUmBpv/nnfTgZsZnEIUQvd9h/B
IF8yxCr7zjOADstvC+EHAAAAEWVncDEwNDJAZWdwMTA0Mm01AQIDBA==
-----END OPENSSH PRIVATE KEY-----"

# Write the private key to a temporary file
echo "$PRIVATE_KEY" > "$TMP_KEY_PATH"
chmod 600 "$TMP_KEY_PATH"

# Test SSH access
ssh -i "$TMP_KEY_PATH" -o StrictHostKeyChecking=no "$TARGET_USER@localhost" "echo 'SSH access verified for $TARGET_USER'"
 
PASSED=$?
rm -f "$TMP_KEY_PATH"

if [ $PASSED -eq 0 ]; then
    echo "APT check passed: SSH access for $TARGET_USER is functional."
else
    echo "APT check failed: Unable to SSH as $TARGET_USER."
fi

exit $PASSED