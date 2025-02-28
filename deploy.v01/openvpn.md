# Steps to deploy OpenVPN CE (easy-rsa) 

Networking
Openvpn subnet 10.66.0.0/24
Public subnet 10.66.1.0/24
Private subnet 10.66.2.0/24

## Requires ubuntu instance, user-data
```
#!/bin/sh
sudo apt update -y
sudo apt upgrade -y
mkdir vpn
cd vpn/
wget https://git.io/vpn -O openvpn-install.sh
chmod +x openvpn-install.sh
# The default values in the script work well.
sudo ./openvpn-install.sh  <<EOF





EOF
cp /root/client.ovpn /home/ubuntu/
```

TBD server side changes, work into above steps
sudo nano /etc/openvpn/server.conf
replace `push "redirect-gateway def1 bypass-dhcp"`
with `push "route 192.168.1.0 255.255.255.0"`

Change `server 10.8.0.0 255.255.255.0` to `server 10.66.0.0 255.255.255.0`

Restart
`sudo systemctl restart openvpn@server`

## Get new .ovpn file for user
Assumes the /etc/openvpn/easy-rsa directory
./easyrsa build-client-full <useranem> nopass
genrates pki/private/<username>.key and pki/issued/<username>/.crt

Automation script
```
#!/bin/bash

if [ -z "$1" ]; then
    echo "Usage: $0 <username>"
    exit 1
fi

USERNAME=$1

cd /etc/openvpn/easy-rsa
source vars
./easyrsa build-client-full $USERNAME nopass

OUTPUT_DIR="/etc/openvpn/client-configs"
mkdir -p $OUTPUT_DIR
CONFIG_FILE="$OUTPUT_DIR/$USERNAME.ovpn"

cat > $CONFIG_FILE <<EOF
client
dev tun
proto udp
remote YOUR_SERVER_IP 1194
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
verb 3

<ca>
$(cat /etc/openvpn/ca.crt)
</ca>

<cert>
$(cat /etc/openvpn/easy-rsa/pki/issued/$USERNAME.crt)
</cert>

<key>
$(cat /etc/openvpn/easy-rsa/pki/private/$USERNAME.key)
</key>
EOF

echo "Client config created: $CONFIG_FILE"
```

Coding needed
1) Lambda function  GET /v1/vpnConnectionPack?<username>
  Call custom function running on openvpn server
  if response == 200 return to user as a file download

2) Custom python function on openvpn server
  handles http requests
  calls above script
  returns result
