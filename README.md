# Nadialin

Cloud based "king-of-the-hill" style cybersecurity practice environment.  
> [!NOTE]
> 'nadialin' is Abenaki for 'the hunter'

### What is a "King-of-hill" event?
- Everyone (squads or individuals) are given access to a system they own.
- At the start all systems are indentical and insecure.
- A squad secures their system and as a by-product understands how to attack other systems.
- A specific file "flag" on the system indicates ownership of that system.
- You want to control the ownership of the flag on as many systems as possible.
- Points are scored by periodic polling of flags and services on all systems.
- Most points in given time frame wins.

> [!WARNING]
> As of June 2025 this repo is once again under active development.  The ultimate goal of this effort is to allow cybersecurity clubs to host staged events.
> __Expect broken items__ 

### What the event organizer needs to know
[Planning and deployment steps.](website/docs/admin_readme.md)
### What the squads/hunters need to know
[Instructions, FAQs, and rules.](website/docs/hunters_readme.md)
## Phases to running a Nadialin event


## Configuring launch templates
### General recomendations
- Create both regular and overprivleged users
- Mismanage authenticatiion
- Manage the boot process. Template commands run once at creation time, not on reboot
- You own the boot process; think cron, think pwn'd processes

