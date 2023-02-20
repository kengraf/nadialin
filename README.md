# Nadialin
Cloud based blue team on-demand practice environment  
Machine types to consider: Firewall, VPN, RDP gateway(Guacamole), API Gateway, WWW, Apps, DBs, AD, Fileshare, Workstation, Kali, Ci/CD (Jenkins, Ansible), Docker/K8s, DNS, Logging (ELK)

## TODO: Automate running the environment as a lower cost, time constrained fleet
```
#!/bin/bash
STOP_TIME=$(date +%Y-%m-%dT%T.000-1)
echo $STOP_TIME
#

aws ec2 create-fleet --type request --terminate-instances-with-expiration  \
        --cli-input-json file://$1  --valid-until $STOP_TIME 

```

Example --cli-input-json file
```
{
    "LaunchTemplateConfigs": [
            {
                    "LaunchTemplateSpecification": {
                    "LaunchTemplateId": "lt-00f89655b42342f30",
                    "Version": "$Latest"
                    },
                    "Overrides": [
                            {
                                    "InstanceType": "t2.micro"
                            }
                    ]
            }
    ],
    "TargetCapacitySpecification": {
            "TotalTargetCapacity": 1,
            "DefaultTargetCapacityType": "spot"
    }
}

```

The template referenced above configured Docker with the EC2 user data
```
#!/bin/sh
yum -y update
yum -y install docker python3-pip 
pip3 install --user docker-compose
usermod -a -G docker ec2-user
id ec2-user
newgrp docker
systemctl enable docker.service
systemctl start docker.service

```

## TODO: automated creating and joining a swarm
