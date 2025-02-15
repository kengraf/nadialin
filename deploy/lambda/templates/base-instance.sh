#!/bin/bash
yum -y update

# Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

set_suqad() {
	python -m http.server 6666
}

set_alice() {
	usermod -aG wheel alice
}

set_bob() {
	echo "bob ALL=(ALL:ALL) ALL" >>/etc/sudoers
}

set_eve() {
	cp /bin/bash /home/eve/tree
	chmod u+s /home/eve/tree
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
/bin/systemctl restart sshd

# Create some users and the sqaud
for user in "[[SQUAD]]" "alice" "bob" "eve" 
do
	createUser $user
done
set_squad
set_alice
set_bob
set_eve

