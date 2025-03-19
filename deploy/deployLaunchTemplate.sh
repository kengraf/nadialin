#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

echo '---IMPORTANT--- Run this script ONCE to create the template'
echo '                Template modifications are done in the AWS console'

echo 'IAM roles were defined in CloudFormation deploy/iam.yaml'

echo "Creating base user-data"
cat <<EOF >user-data.sh
#!/bin/bash
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
set_squad() {
pushd /home/$1
nohup python3 -m http.server [[GET_FLAG_PORT]] > server.log 2>&1 &
popd
}

# Create user function
create_user() {
useradd --password $(openssl passwd passwordsAREwrong) \$1
pushd /home
chmod 755 \$1
cd $1
mkdir .ssh
cd .ssh
# Create scoring keys
ssh-keygen -t rsa -b 1024 -f scoring_rsa -N ""
cp scoring_rsa.pub authorized_keys
chmod 440 scoring_rsa
cd /home/\$1
echo \$1 > flag.txt
chown -R \$1:\$1 .
ls -ltrRa
popd
}

create_user [[SQUAD]]
set_squad  [[SQUAD]]

EOF

# Add event cusmtomizations to EC2 templates
cat <<EOF >>user-data.sh
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
	create_user \$user
 	\$user
done
EOF

cat <<EOF >launch-template-config.json
{ 
  "IamInstanceProfile": { "Name": "${DEPLOYNAME}-SSMInstanceProfile" },
  "ImageId": "ami-088b41ffb0933423f",
  "SecurityGroupIds": ["sg-05a87a5fbfd0fd5ae"],
  "InstanceType": "t2.micro",
  "UserData": "$(base64 -w 0 user-data.sh)"
}
EOF

echo "Creating base template"
aws ec2 create-launch-template \
    --launch-template-name "${DEPLOYNAME}-base-template" \
    --version-description "Basic ${DEPLOYNAME} template" \
    --launch-template-data file://launch-template-config.json

