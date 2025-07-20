pushd /home/wooba/.ssh
scp -i scoring_key ec2-user@localhost:./.ssh/authorized_keys pub
