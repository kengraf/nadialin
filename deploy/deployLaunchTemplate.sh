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
useradd --password \$(openssl passwd passwordsAREwrong) \$1
pushd /home
chmod 755 \$1
cd \$1
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

yum install -y sshpass
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
/bin/systemctl restart sshd
EOF

# Add event cusmtomizations to EC2 templates
cat <<EOF >>user-data.sh
# Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

# Create some users and their special sauce
alice() {
# Create liveness keys
cat <<EOF >>authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCyxVuv0OLHeugIw9/oM+1A9c3S6l9xA+CiknNXqFjyz1c9RytfOdCpDFPDexdiv7QPHGypn+HdzgNpRdf6/8afG/anhRjS0jMGBPsVfTCDaaWN++/0Qk9SlKj3N5jEo+QuRwGtSZ1IPWeltfQRnoU0cM7jnigrCnkDkzF7cKBCUQ== cloudshell-user@ip-10-134-93-242.us-east-2.compute.internal
EOK
cat <<EOF >>alice_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEAssVbr9Dix3roCMPf6DPtQPXN0upfcQPgopJzV6hY8s9XPUcrXznQ
qQxTw3sXYr+0DxxsqZ/h3c4DaUXX+v/Gnxv2p4UY0tIzBgT7FX0wg2mljfvv9EJPUpSo9z
eYxKPkLkcBrUmdSD1npbX0EZ6FNHDO454oKwp5A5Mxe3CgQlEAAAIwu7AzP7uwMz8AAAAH
c3NoLXJzYQAAAIEAssVbr9Dix3roCMPf6DPtQPXN0upfcQPgopJzV6hY8s9XPUcrXznQqQ
xTw3sXYr+0DxxsqZ/h3c4DaUXX+v/Gnxv2p4UY0tIzBgT7FX0wg2mljfvv9EJPUpSo9zeY
xKPkLkcBrUmdSD1npbX0EZ6FNHDO454oKwp5A5Mxe3CgQlEAAAADAQABAAAAgFyHfDJfGt
IHEoxe3ciw/88MqvDNMIMtb5qV1K99SjS7Drt/17odEZw97ikS0ALjmI3tt2yAfYaxd+CI
LwcSVjnrtDUU1TubJd84BPQN/5G15JdInG2huR1DZ8lE0mtlSJ5HxCD0x7PgThwln+oBlM
W91kcAvAcpUw1zgID9o6wBAAAAQHc1NGQ/mteX8mXdRHsmGVIrlTRK0FHny2gr+xJgAWTc
+G4N3cVyHhfEhWOw8JUrxF9H6dwFGDgwIoRvZt23bf0AAABBAO16esJU7jB432FjgpSdt3
6VgpL0D9QsO7LlwU3xw7z/j6Yl97pgOHG8SKvmKeTNCxz8a0bSy15DtuDyCb8CiMEAAABB
AMC2t9fbRxvmrNb0jypiuYXXOtVl5RfcvpBHHG37nkXqo0oaXba4HBbpnWL09x4UkkVLTE
RSjzsbqCGDR6f/DZEAAAA7Y2xvdWRzaGVsbC11c2VyQGlwLTEwLTEzNC05My0yNDIudXMt
ZWFzdC0yLmNvbXB1dGUuaW50ZXJuYWw=
-----END OPENSSH PRIVATE KEY-----
EOK
chmod 440 alice_rsa
usermod -aG wheel alice
}

bob() {
# Create liveness keys
cat <<EOF >>authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQC5rKdFyxoC+Qz1HW7OYacMSNcjqhM0qdEQuaUUWsVYkDXZGd4zIy95E87GOPZ4tNncR49NMuZzOPJd7r9ZuXQf7fh3aCeG2OIeDbuqmTbkzTr/5HiBssNGbsOxd23uYopWrx2U6Z18damSfhqDGm9fpekJ24jWhUAWAWX6z+9x0Q== cloudshell-user@ip-10-134-93-242.us-east-2.compute.internal
EOK
cat <<EOF >>bob_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEAuaynRcsaAvkM9R1uzmGnDEjXI6oTNKnRELmlFFrFWJA12RneMyMv
eRPOxjj2eLTZ3EePTTLmczjyXe6/Wbl0H+34d2gnhtjiHg27qpk25M06/+R4gbLDRm7DsX
dt7mKKVq8dlOmdfHWpkn4agxpvX6XpCduI1oVAFgFl+s/vcdEAAAIwen9qo3p/aqMAAAAH
c3NoLXJzYQAAAIEAuaynRcsaAvkM9R1uzmGnDEjXI6oTNKnRELmlFFrFWJA12RneMyMveR
POxjj2eLTZ3EePTTLmczjyXe6/Wbl0H+34d2gnhtjiHg27qpk25M06/+R4gbLDRm7DsXdt
7mKKVq8dlOmdfHWpkn4agxpvX6XpCduI1oVAFgFl+s/vcdEAAAADAQABAAAAgHYh/HcyZs
VXccAOTu6uQNtXCNKfJgMOvH6YrwhJTGAxuKD9jVsZ2t19FcUWfvKDlk1Jlko2xVqv87yB
52sNzGxiYEqhZ9k60l9Z4HD6g/BppVfSjhj+njdFXHyOd4r19tleE7uxk3/pIXJo5L6b8N
kPGTpEumwdCP9/xPdxVvblAAAAQAE7fKt7xX9J4MAicxaCIpOJy2t84pq3uKFEZTgTAN6/
3cd+1pBlwCNHILFo7NPUR048joW+g6hfbumylDfvpQ4AAABBAOZwxTyArZJmipJiyw7p54
n0IXnz580FJTyjhqrpnvb8oc/ol0vVZ00LgRZZERHNDh12NEyrlkeNvoDC8x8X73cAAABB
AM5ExmoWfG3h7VnKLds59QtldY9GnPNVliAxjgneWZcYpF6KTQXrSjTbg+Y5Dw9vENEI06
rYEGL+XUTY5A4ZSvcAAAA7Y2xvdWRzaGVsbC11c2VyQGlwLTEwLTEzNC05My0yNDIudXMt
ZWFzdC0yLmNvbXB1dGUuaW50ZXJuYWw=
-----END OPENSSH PRIVATE KEY-----
EOK
chmod 440 bob_rsa
echo "bob ALL=(ALL:ALL) ALL" >>/etc/sudoers
}

eve() {
# Create liveness keys
cat <<EOF >>authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQDSZF1/k7nNeZijsPZ2Q272fkHZ2S0VGPN6xUVQGU4nUvvhyXi8wR1iYInrXt0ucq77gvrP97AE7JXL0AXY2tVlR2a/cs3CqYri0oFlptb8fbRPVGmS57NUFVeTcr74riZOQgGA1XTwVyNL6lsKcdYDyNLaisU8/ZULdwSDc0Zj0Q== cloudshell-user@ip-10-134-93-242.us-east-2.compute.internal
EOK
cat <<EOF >>eve_rsa
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAlwAAAAdzc2gtcn
NhAAAAAwEAAQAAAIEA0mRdf5O5zXmYo7D2dkNu9n5B2dktFRjzesVFUBlOJ1L74cl4vMEd
YmCJ617dLnKu+4L6z/ewBOyVy9AF2NrVZUdmv3LNwqmK4tKBZabW/H20T1RpkuezVBVXk3
K++K4mTkIBgNV08FcjS+pbCnHWA8jS2orFPP2VC3cEg3NGY9EAAAIwkIrLmZCKy5kAAAAH
c3NoLXJzYQAAAIEA0mRdf5O5zXmYo7D2dkNu9n5B2dktFRjzesVFUBlOJ1L74cl4vMEdYm
CJ617dLnKu+4L6z/ewBOyVy9AF2NrVZUdmv3LNwqmK4tKBZabW/H20T1RpkuezVBVXk3K+
+K4mTkIBgNV08FcjS+pbCnHWA8jS2orFPP2VC3cEg3NGY9EAAAADAQABAAAAgFoS8hyeiF
u6BWl/Z+U19Zm+cD7uRejUZ9lV/9jNHLKlSoVeFjzpiMUHg8SrNpKeMuAnMW48IrXY/EDn
7Ljs55LPn+pQWJwi6dhzQFfCgFzTi7Pd59LDGCjcviJ1SVolX1rgP7cvwGMTZr27DPwLFJ
8d2+3oZx1igv2ZNFakXLgpAAAAQDeVJ7r+12VH+xTwM/5Gg+gOKBVuJBXo7dYJAr89nEVx
BQ4hxZk/ljtSkKM0QEUD6ETWDlrdp955ZB0vFuPvQ6EAAABBAPdzfeze7G306273IRUTzl
TPYlPv9YbT5sNoBpq0PT1QMlQkw1YDOu6kwqC+sGQiEAIZdrCHyn4uST5OTxinFScAAABB
ANmpHX/ZFLfMre5Tln6sinC2lNmJbfrudrWiHQH6NGr3EARR7vkIrzAExp7lHU49YCDEog
UmWOrg0WbqgSKECkcAAAA7Y2xvdWRzaGVsbC11c2VyQGlwLTEwLTEzNC05My0yNDIudXMt
ZWFzdC0yLmNvbXB1dGUuaW50ZXJuYWw=
-----END OPENSSH PRIVATE KEY-----
EOK
chmod 440 eve_rsa
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

