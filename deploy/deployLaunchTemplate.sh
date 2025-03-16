#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

echo '---IMPORTANT--- Run this script ONCE to create the template'
echo '                Template modifications are done in the AWS console'

echo 'Defining role (if needed)'
aws iam create-role --role-name ${DEPLOYNAME}-SSMRole \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": { "Service": "ec2.amazonaws.com" },
                "Action": "sts:AssumeRole"
            }
        ]
    }'

echo 'Attaching policy to role'
aws iam attach-role-policy --role-name ${DEPLOYNAME}-SSMRole \
    --policy-arn arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore

echo 'Creating profile to role'
aws iam create-instance-profile --instance-profile-name \
    ${DEPLOYNAME}-SSMInstanceProfile

echo 'Attaching policy to profile'
aws iam add-role-to-instance-profile --role-name ${DEPLOYNAME}-SSMRole \
    --instance-profile-name ${DEPLOYNAME}-SSMInstanceProfile 

echo 'Creating template"
aws ec2 create-launch-template \
    --launch-template-name ${DEPLOYNAME}-template \
    --version-description "Basic ${DEPLOYNAME} template" \
    --launch-template-data '{ 
        "IamInstanceProfile": { "Name": "${DEPLOYNAME}-SSMInstanceProfile" },
        "ImageId": "ami-088b41ffb0933423f",
        "SecurityGroupIds": ["sg-05a87a5fbfd0fd5ae"]
        "InstanceType": "t2.micro",
        "UserData": "`$(echo -n "#!/bin/bash
sudo yum install -y amazon-ssm-agent
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent" | base64)`"
    }'
