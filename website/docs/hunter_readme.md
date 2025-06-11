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
- The machines you are given will die at the end of the event sooooo....  Yes you can: __rm -rf /__ or __:(){ :|:& };:__ but, do you really want to?  Destorying things will only take away your opprotunity to score more points.

> "Hell, there are no rules here - we're trying to accomplish something." - Thomas A. Edison
- Feel free to experiment, no one is going to be upset at the end of the event if a machine is not working.

## Creating your backdoor
- The event determines the virtual machine size, OS, and command shell.  The default is t2.micro, running AWS Linux 2023, and /bin/bash
- Your can assume the following commands have run prior to backdoors being defined:
```
yum update -y
yum upgrade =y
yum install -y nginx
/bin/systemctl start nginx.service
```
&& yum upgrade" has been run and the 
- Create a shell script with two functions.  One to load your backdoor and the other to test if the backdoor is still working.  Example assuming you are the bear squad.
```
# This script runs as root and can assume a user with your squad name has already been created
create_bear() {
    pushd /home/bear
    # Do your thing(s)
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



 
