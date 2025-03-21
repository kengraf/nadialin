#!/bin/bash
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
set_squad() {
pushd /home/
nohup python3 -m http.server [[GET_FLAG_PORT]] > server.log 2>&1 &
popd
}

# Create user function
create_user() {
useradd --password $(openssl passwd passwordsAREwrong) $1
pushd /home
chmod 755 $1
cd $1
mkdir .ssh
cd .ssh
# Create scoring keys
ssh-keygen -t rsa -b 1024 -f scoring_rsa -N ""
cp scoring_rsa.pub authorized_keys
chmod 440 scoring_rsa
cd /home/$1
echo $1 > flag.txt
chown -R $1:$1 .
ls -ltrRa
popd
}

create_user [[SQUAD]]
set_squad  [[SQUAD]]

# Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

# Create some users and their special sauce
alice() {
usermod -aG wheel alice
}

bob() {
echo "bob ALL=(ALL:ALL) ALL" >>/etc/sudoers
}

eve() {
pushd /home/eve/.ssh
cat authorized_keys >> /home/[[SQUAD]]/.ssh/authorized_keys
popd
}

for user in "alice" "bob" "eve" 
do
	create_user $user
 	$user
done
