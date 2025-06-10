#### What does "Nadialin" mean?
- It's Abenaki for "the hunter".  Are you a nadialin ready for a threat hunt?
#### What is the background image a painting of?
- Fort Niagara; the "French Castle" in 1723.  [State park link](https://www.oldfortniagara.org/)  
- The author has fond memories of being able to climb a tree in his grandmother's orchard and being able to see the fort.
#### Can a "squad" be a single hunter?
- Yes, being a lone wolf is awesome!
#### How long is an event?
- No design limit; experience says 1 or 2 hours is best.
#### Are cloud providers other than AWS supported?
- No.
#### Do the hunters need an AWS account?
- Only the event admin needs an AWS account.
#### Can the event admin also be a hunter?
- Yes, but ideally no, as the event admin has advanced knowledge of machine security flaws.
#### Does the event admin need AWS knowledge?
- Scripts are provided, so knowledge of how to use CloudShell and the EC2 launch process should be enough knowledge to run an event.
#### The number of hunters allowed per squad?
- This is set by the event admin.
#### Event size limit?
- In theory no limit, but then the author has only run events with dozens of squads.  The first thing to most likely to be overrun (if deployed) would be the OpenVPN server.

#### What does it cost to run an event?
- Assuming an event with dozens of squads.  Communications, lambda requests, and database would all run in the AWS free-tier.  The machines assigned to each squad run on EC2 instances and do incur hourly costs.  Assuming you are no longer in the free-tier.  An hour long event for 20 squads would cost less than a dollar.
#### Can I build my own flawed system(s) to use in an event?
- Yes, and it is highly encouraged!  [Ideas](./backdoor_building.md)
