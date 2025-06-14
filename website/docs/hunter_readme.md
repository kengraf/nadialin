# Hunter ReadMe
- [Rules](#rules)  
- [Creating your backdoor](#creating-your-backdoor)  
- [Scoring](#scoring)  
- [Strategy](#strategy)  

## Rules
> "You make all the rules, in this game of fools" - Face-2-Face: 10-9-8

> "Bollocks to the rules!" - Lord of the Flies
- Attack your friends, attack your enemies, attack yourself!   Just __DO NOT ATTACK THE INFRASTRUCTURE!__


> Rules are not necessarily sacred, principles are. - Franklin D. Roosevelt

> I follow three rules: Do the right thing, do the best you can, and always show people you care. - Lou Holtz
- The machines you are given will die at the end of the event sooooo....  Yes you can: `rm -rf /` or `:(){ :|:& };:` but it not in your best interest.  Destroying things will only take away your opportunity to score more points.

> "Hell, there are no rules here - we're trying to accomplish something." - Thomas A. Edison
- Feel free to experiment, no one is going to be upset at the end of the event if a machine is not working.

## Creating your backdoor
- The event admin determines the virtual machine size, OS, and command shell.  The default is t2.micro, running AWS Linux 2023, and /bin/bash
- You can assume the OS is current and fully patched.
- When a VM is created a shell script referred to USER-DATA is executed. The script executes with root permissions. Example:
```
  # Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

# Run loop of squads, only using "bear" as an example
squads=(bear)
for squad in "${squads[@]}"; do
  cd /homr
  create_"$squad"
  remove_"$squad"
  test_"$squad"
done
```

- You need to create three shell functions.  Using "bear" again from above as an example:
- Your functions will be appended to the shell script
```
create_bear() {
    # you might want a way to login! :-)
    useradd bear
    pushd /home/bear
    mkdir .ssh
    cd .ssh
    ssh-keygen -t rsa -b 1024 -f bear -C bear -N ""
    cp bear.pub authorized_keys
    chmod 440 bear
    cd ..
    chown -R bear:bear .
    popd
}
test_bear() {
  # Only use full file paths
  if grep -q "bear" "/home/.ssh/authorized_keys"; then
    return 0  # true your string found in file
  else
    return 1 
  fi
}
delete_bear() {
  # Complete remove all changes made by your create_SQAUD function
  userdel -r bear
}
```
### Your backdoor must be:
- __TESTD:__  Launch your own VM and make sure your backdoor executes as excepted.
- __SELF-CONTAINED:__  No 3rd party installs or custom executables.  Bash scripts and python3 code is allowed.
- __USER_SPACE:__  No kernel level exploits.
- __ADDITIVE:__  Meaning you can change system files, but your changes can not remove or alter existing functionality.  An example might be, Nginx is running by default. You want to add a website to allow ingress.  You should create an additional virtual website and NOT attempt to reinstall nginx or change the behavior of the existing website(s).

### Resources: Ideas for possible backdoors
- [Github: Linux backdoor concepts](https://github.com/gquere/linux_backdooring)
- [Linux Backdoors and Where to Find Them](https://fahmifj.github.io/articles/linux-backdoors-and-where-to-find-them/)
- [Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
## Scoring
Every minute a set of requests are made for every VM in the competition.  Point values are set by the event admin.
- Ownership: Points go to the squad named in the VM flag file.
- User liveness: Points are scored for the VM owner if unprivleged users have access to the VM.
- Squad liveness: Points are scored for the squad if their backdoor is operational.
- VM rebuild: Points are deducted if a squad requests a rebuild of their VM.

## Strategy
### Red Team (attackers)
A complete backdoor works on three levels: Ingress, Escalation, and Persistence.


 
