#1/bin/bash
# This script comfirms SSH ccess is still active
# Removal of user or SSH files will cause a failure
scp -i scoring_key example@localhost:./.ssh/authorized_keys pub
