#!/bin/bash
# Squad: hawk
# Purpose: Completely remove all APT components and undo system changes

# Remove sudoers entry
rm -f /etc/sudoers.d/hawk_access

# Remove persistence marker
rm -f /var/tmp/.hawk_apt_active

# Remove user and all associated files
userdel -r -f hawk 2>/dev/null

# Clean up any remaining files that might not have been removed
rm -rf /home/hawk 2>/dev/null

