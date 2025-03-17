#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

echo '---IMPORTANT--- Run this script ONCE to create the template'
echo '                Template modifications are done in the AWS console'

echo 'Defining role (if needed)'
aws iam create-role --role-name ${DEPLOYNAME}-SSMRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": { "Service": "ec2.amazonaws.com" },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

echo 'Attaching policy to role'
aws iam attach-role-policy --role-name ${DEPLOYNAME}-SSMRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

echo 'Creating profile to role'
aws iam create-instance-profile --instance-profile-name \
    ${DEPLOYNAME}-SSMInstanceProfile

echo 'Attaching policy to profile'
aws iam add-role-to-instance-profile --role-name ${DEPLOYNAME}-SSMRole \
    --instance-profile-name ${DEPLOYNAME}-SSMInstanceProfile 

echo "Creating base user-data"
cat <<EOF >user-data.sh
#!/bin/bash
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
EOF

cat <<EOF >>user-data.sh
# Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

set_squad() {
pushd /home/$1
nohup python3 -m http.server [[GET_FLAG_PORT]] > server.log 2>&1 &
popd
}

set_alice() {
usermod -aG wheel alice
}

set_bob() {
echo "bob ALL=(ALL:ALL) ALL" >>/etc/sudoers
}

set_eve() {
pwd
}

# Create user
createUser() {
useradd --password $(openssl passwd passwordsAREwrong) $1
pushd /home
chmod 755 $1
cd $1
mkdir .ssh
cd .ssh
ssh-keygen -t rsa -b 1024 -f id_rsa -N ""
cp id_rsa.pub authorized_keys
cp id_rsa.pub /home/[[SQUAD]]/.ssh/authorized_keys
chmod 440 id_rsa
cat <<EOT >> authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDOsXCYNTw6uN3fXlpp8xcd4JtaGZAoLXnmwLX37Bh2THgUbeT0AeT5YBbSUzdgx0Ql21K9fZXjnbd4GIwP1624Swf2Qok4ZHbOIxQwYOe3s73V3h1htXVwIAUxip8rPs8ebW6Sj+YqvkGHPEYt71eX/ylye2xTxCNdeb9HP1oQz5mcRwKVXvD8VQ7n6sM9aduY5mHZgjEWBQ4Ql3nw0QmWLZu0/OvR/QVU/pXwx+zuBUAqayAY77PIV+fsA5XMhGUOjwfI1UPARpqxm1j+8ywt/L4UQLuuWbnBZ3DRAE/dauyL5s7WaekdGxtPudeyjDeWpwPbkyHOeE/txnIsv3UTXiip/u1wdYdu9ajCi8uLF3XXr+O7j0fIdBUvPyHAFguTBgyoxNjAalMsCnTuQRtANdgZQBxR29yXegN3DkuGRLc9+02NZsxW8FkRcPsBpoDnrqZ7Z7xNAy4XlAsoMnxhLQ775/vaOv7Le9PLaELXZV7DHwuM+9n4lmMRUxE+7CKPB8ulgwNpmWRv8SlDjBXVhYb/g2BkTyAziytqCBQR7QNKI9P6aFZCA60lCo3kv7SEEruadJdIZtYoZ7w4rNeCT7/5AeIzGyvaXbIecNqqLhtPx75jwvveI+AuvlHYTo5ZzeXl2QiSKgaJkw1Yyho/SK4O9nkouBtqy1lf9Yhb4w== ec2-user@amazonaws.com
EOT
cd /home/$1
echo $1 > flag.txt
chown -R $1:$1 .
ls -ltrRa
popd
}

# Allow password logins (why would you do that?)
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sed -i 's/#Port 22/Port 10022/g' /etc/ssh/sshd_config
/bin/systemctl restart sshd

# Create some users and the sqaud
for user in "[[SQUAD]]" "alice" "bob" "eve" 
do
	createUser $user
done
set_squad  [[SQUAD]]
set_alice
set_bob
set_eve
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

