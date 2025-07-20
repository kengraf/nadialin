# Hunter ReadMe
- [Objective](#objective)
- [Rules](#rules)  
- [Creating your backdoor](#creating-your-back-door)  
- [Scoring](#scoring)  
- [Strategy](#strategy)  
## Objective
- Each squad is given ownership of a compromised system.  A file in the squads home directory flags the current owner.
- Changing the flag to your squad on another machine indicates your ownership of that machine.
- You want to own as many machines as possible.
  
## Rules
> "You make all the rules, in this game of fools" - Face-2-Face: 10-9-8

> "Bollocks to the rules!" - Lord of the Flies
- Attack your friends, attack your enemies, attack yourself!


> Rules are not necessarily sacred, principles are. - Franklin D. Roosevelt

> I follow three rules: Do the right thing, do the best you can, and always show people you care. - Lou Holtz
- The machines you are given will die at the end of the event sooooo....  Yes you can: `rm -rf /` or `:(){ :|:& };:` but it not in your best interest.  Destroying things will only take away your opportunity to score more points.

> "Hell, there are no rules here - we're trying to accomplish something." - Thomas A. Edison
- Feel free to experiment, no one is going to be upset at the end of the event if a machine is not working.

## Creating your back door
- The event admin determines the virtual machine size, OS, and command shell.  The default is t3.micro, running AWS Linux 2023, and /bin/bash
- You can assume the OS is current and fully patched.
- When a VM is created a shell script referred to as USER-DATA is executed. The script executes with root permission. Example:
```
  # Setup web server
yum install -y nginx
/bin/systemctl start nginx.service

# Run loop of squads, only using "bear" as an example
squads=(bear)
for squad in "${squads[@]}"; do
  cd /home
  create_"$squad"
  remove_"$squad"
  test_"$squad"
done
```

- You need to create three shell functions.  Using "bear" again from above as an example:
- Your functions will be executed when the VM is launched.
```
create_bear() {
    # you might want a way to login! :-)
}
test_bear() {
  # Only use full file paths
  if grep -q "bear" "/home/some-file-you-created"; then
    return 0  # true if the word bear found in file
  else
    return 1 
  fi
}
delete_bear() {
  # Complete remove all changes made by your create_bear function
  userdel -r bear
}
```
### Your backdoor (create_bear) must be:
- __TESTED__: Launch your own VM and make sure your backdoor executes as excepted.
- __SELF CONTAINED__: No 3rd party installs or complied code.  Bash scripts and python3 code is allowed.
- __LIMITED COMPLEXITY__: Maximum one access method and one escalation method.
- __USER SPACE__:  No kernel level exploits.
- __ADDITIVE__:  Meaning you can change system files, but your changes cannot remove or alter existing functionality.  An example might be wanting to add a website to allow ingress.  Nginx is running by default.   You should create an additional virtual website and NOT attempt to reinstall nginx or change the behavior of the existing website(s).

### Resources: Ideas for possible backdoors
- [Github: Linux backdoor concepts](https://github.com/gquere/linux_backdooring)
- [Linux Backdoors and Where to Find Them](https://fahmifj.github.io/articles/linux-backdoors-and-where-to-find-them/)
- [Privilege Escalation](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
## Scoring
Every minute a set of requests are made for every VM in the competition.  Point values are set by the event admin.
- __Ownership__: Points go to the squad named in the VM flag file.
- __User liveness__: Points are scored for the VM owner if unprivileged users have access to the VM.
- __Squad liveness__: Points are scored for the squad if their backdoor is operational.
- __VM rebuild__: Points are deducted if a squad requests a rebuild of their VM.

## Strategy
Working as a team the best approach is to divide tasks by skill set.  You are free to select tools and processes to obtain your goals.

### Red Team (attacking)
A complete backdoor works on three levels: Access, Escalation, and Persistence.  Given you have escalated access when your backdoor is loaded, your backdoor may have any one or more of these three levels.
- __ACCESS__: Typically but not limited to; SSH, HTTP, or Telnet to activate a command shell as a user.
- __ESCALATION__: SUDO, SUID, or system configuration errors that allow an unprivileged user access to resources they should not have.
- __PERSISTANCE__: This is what separates good from great backdoors.  Stealth may help delay detection, recovery may foil attempts at removal, triggers/delays maybe avoid initial security scans.

### Blue Team (defending)
- __USER ACCESS__: It is a crisis for any business when authorized users are denied access.  The authorized users are defined by the event admin and liveness tests are sent to the VM to make sure authorized users have access.  Interfering with their access is equivilent to the machine being down.
- __IDENTIFY__: Open ports, unknown processes, suspicious files/network behavior.

### White Team (administration)
- __MONITOR__: Network traffic, user access, file system changes, changes in processes.
- __HARDEN__: Removal of unapproved; users, configurations, processes, and files.
- __MAINTAIN__: Limitations on user, network and network behavior.
