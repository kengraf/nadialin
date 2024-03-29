
### TODO: Add CloudFront rather than serving via S3. [notes](https://github.com/aws-samples/amazon-cloudfront-secure-static-site)

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
