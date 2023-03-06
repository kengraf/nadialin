# Nadialin
Cloud based blue team on-demand practice environment.  

## NOTE: 'nadialin' is Abenaki for 'the hunt'
The ultimate goal of this effort is to allow 'blue team' members a practice site to hunt for staged cyber attacks.  
While effort was made to minimize the number of times 'nadialin' was used in scripts and templates; You should be able to load the code base into your favorite IDE and make a global replace.

The practice environment will be templated to allow for various scenarios.  
In a scenarios many different machine types are expected: Firewall, VPN, RDP gateway (Guacamole), API Gateway, WWW, Apps, DBs, AD, Fileshare, Workstation, Kali, Ci/CD (Jenkins, Ansible), Docker/K8s, DNS, Logging (ELK)

Access to machines in a scenario will only be provided via a VPN using RDP.

Substantial AWS infrastructure is needed to support the creation, monitoring, and release of AWS resources.

## This repo focuses on the automation resources using CloudFormation
List of major AWS components
- S3 : GitHub action is used push to a public bucket, TODO: Leverage CloudFront
- Cognito : User management
- API Gateway : Front user interaction with Lambda based features
- VPN : Control user access to scenarios
- Scenario : Templated deployment the machines the user will work with

## Step 1: S3 deployment of artifacts from your repo

1. Clone this repo
2. Create S3 bucket
This command with create an S3 bucket named the same as the stack-name.
```
aws cloudformation create-stack  --stack-name nadialin --template-body file://templates/storageStack.json
```
3. In your GitHub repo settings, add secrets for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.  
You care about security right?  Best to create a role, user, and access key limited to writing your S3 bucket.  No need to give the Github action extra powers.

At this point you should confirm your bucket is populated and publicly flapping in the breeze.



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
