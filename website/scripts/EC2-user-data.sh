#!/bin/bash
# ----------------------------------------
# NOTE
# [[item]] constructs are replaced with proper runtime values
# before the template is used to launch an instance
#
# ----------------------------------------
# Define common users and services
yum -y update
yum install -y python3 nginx
/bin/systemctl start nginx.service
#
# Allow password logins for scoring checks of known users
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
/bin/systemctl restart sshd
#
# Create 'normal' users
useradd --password $(openssl passwd passwordsAREwrong) gooba
useradd wooba
su -c 'ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -q' wooba
su -c 'mv ~/.ssh/id_rsa.pub ~/.ssh/authorized_keys' wooba
cp /home/wooba/.ssh/id_rsa /home/ssm-user/.ssh/wooba
chown ssm-user:ssm-user /home/ssm-user/.ssh/wooba

#
# ----------------------------------------
# Define shell variables
GET_FLAG_PORT=[[GET_FLAG_PORT]]
SQUAD=[[SQUAD_NAME]]
SQUAD_LIST=[[SQUAD_LIST]]
SAUCE_LOCATION=[[SAUCE_LOCATION]]
#
# ---------------------------------------
# Invoke each squad's "special create sauce"
#
for squad in "${SQUAD_LIST[@]}"; do
  curl -sL $SAUCE_LOCATION/create_$squad.bash | sed 's/\r$//' | bash
done
# ----------------------------------------
# Ensure the owner squad and directory exists
#
id $SQUAD >/dev/null 2>&1
if [ $? -ne 0 ]; then
    adduser $SQUAD
fi
[ ! -d "/home/$SQUAD" ] && mkdir -p "$SQUAD"
chown -R $SQUAD:$SQUAD /home/$SQUAD
# -----------------------------------------
# Set the flag
# Run a dedicated python process to server content
#
pushd /home/$SQUAD
echo $SQUAD > flag.txt
chown -R $SQUAD:$SQUAD flag.txt
nohup python3 -m http.server $GET_FLAG_PORT > server.log 2>&1 &
popd
# ----------------------------------------
# Ensure no squad has stepped on another
#
for squad in "${SQUAD_LIST[@]}"; do
  curl -sL $SAUCE_LOCATION/test_$squad.bash | sed 's/\r$//' | bash
  if $? then
    echo "Test for $squad failed"
  fi
done



