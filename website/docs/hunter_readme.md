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
- The event determines the virtual machine size, OS, and command shell.  The default is t2.micro, running AWS Linux 2023, and /bin/bash
- You can assume the OS is current and fully patched.
- Your backdoor will be appended to the following shell script that runs as root:
```
  # Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

# Run loop of squads
names=(bear)
for squad in "${squads[@]}"; do
  create_"$squad"
  remove_"$squad"
  test_"$squad"
done
```

- You need to create three shell functions.  Using "bear" from above as an example:
```
create_bear() {
    # you might want a way to login! :-)
    useradd --password $(openssl passwd passwordsAREwrong) bear
    pushd /home
    chmod 755 bear
    cd bear
    mkdir .ssh
    cd .ssh
    ssh-keygen -t rsa -b 1024 -f scoring_rsa -N ""
    cp scoring_rsa.pub authorized_keys
    chmod 440 scoring_rsa
    cd ..
    chown -R bear:bear .
    popd
}
test_bear() {
  if grep -q "string" "file"; then
    return 0  # true your string found in file
  else
    return 1 
  fi
}
```
- Your backdoor must be ADDITIVE.  Meaning you change change system files, but your changes cna not remove or alter exisitng functionality.
- 
## Scoring
blah

## Strategy


# User guide
- TBD



 
