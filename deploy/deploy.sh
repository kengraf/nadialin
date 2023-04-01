#!/bin/bash

STACK_NAME=$1

if [ -z "$1" ]
  then
    echo "No STACK_NAME argument supplied"
    exit 1
fi

S3BUCKET=$STACK_NAME-$(tr -dc a-f0-9 </dev/urandom | head -c 10)
sed -ri "s/nadialin-[0-9a-f]*/${S3BUCKET}/" parameters.json

S3BUCKET=$STACK)NAME
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating stack..."
STACK_ID=$()



# Ideally the CloudFormation stacks would be combined into one.
# This appoach is allow students to alter steps as needed

# 
aws cloudformation create-stack --stack-name nadialin-storage --template-body file://storageStack.json --parameters file://parameters.json --tags file://tags.json --output text
# upload lambda functions
aws s3 cp lambda/post-auth/post-auth.zip s3://${S3BUCKET}/deploy/post-auth.zip
aws s3 cp lambda/default/default.zip s3://nadialin/deploy/default.zip
aws s3 cp lambda/admin/admin.zip s3://nadialin/deploy/admin.zip
aws s3 cp lambda/user/user.zip s3://nadialin/deploy/user.zip
# upload website
cd website
aws s3 sync . s3://nadialin
cd ../deploy
aws cloudformation create-stack --stack-name nadialin-lambda --template-body file://lambdaStack.json --capabilities CAPABILITY_NAMED_IAM --parameters file://parameters.json --tags file://tags.json --output text

aws cloudformation create-stack --stack-name nadialin-lambda --template-body file://lambdaStack.json --capabilities CAPABILITY_IAM --parameters file://parameters.json --tags file://tags.json --output text

aws cloudformation create-stack --stack-name nadialin-identity --template-body file://identityStack.json --capabilities CAPABILITY_IAM --parameters file://parameters.json --tags file://tags.json --output text

aws cloudformation create-stack --stack-name nadialin-web --template-body file://webStack.json --capabilities CAPABILITY_IAM --parameters file://parameters.json --tags file://tags.json --output text

aws cloudformation create-stack --stack-name nadialin-frontend --template-body file://Stack-frontend.json --parameters file://parameters.json --tags file://tags.json --output text

aws cloudformation describe-stacks --stack-name "nadialin" --query "Stacks[*].{StackId: StackId, StackName: StackName}

# Update website config to reflect new resources
VAR=$(aws cloudformation list-exports --query "Exports[?contains(Name,'nadialin-cognito-UserPoolID')].[Value]" --output text)
sed -ri "s/(userPoolId: )('.*')/\1'${VAR}'/i" website/scripts/config.js
VAR=$(aws cloudformation list-exports --query "Exports[?contains(Name,'nadialin-cognito-ClientID')].[Value]" --output text)
sed -ri "s/(userPoolClientId: )('.*')/\1'${VAR}'/i" website/scripts/config.js
VAR=$(aws cloudformation list-exports --query "Exports[?contains(Name,'nadialin-ApiEndpoint')].[Value]" --output text)
sed -ri "s^(invokeUrl: )('.*')^\1'${VAR}'^i" website/scripts/config.js

echo "Waiting on ${STACK_ID} create completion..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_ID}
aws cloudformation describe-stacks --stack-name ${STACK_ID} | jq .Stacks[0].Outputs