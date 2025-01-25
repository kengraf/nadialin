#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

# Ideally the CloudFormation stacks would be combined into one.
# This appoach allows students to alter steps as needed

STACK_NAME="$DeployName-storage"
echo "Creating stack... $STACK_NAME"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file storage.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      S3bucketName=${S3BUCKET} \
      DeployName=${DeployName} \
  --output text
echo "Waiting on ${STACK_NAME} create completion..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs

echo "Packaging and uploading the lambda function"
cd lambda
if [ ! -e "function.zip" ]; then
    echo "Add required library to zip."
    mkdir package
    pip install --target ./package google-auth
    pip install --target ./package requests
    cd package/
    zip -r ../function.zip .
    cd ..
fi
zip function.zip verifyToken.py
aws s3 cp function.zip s3://${S3BUCKET}
cd ..

echo "Uploading website content"
cd ../website
aws s3 sync . s3://${S3BUCKET}
cd ../deploy

echo "Deploying backend components (apigatewayv2, lambda, dynamodb)"
STACK_NAME="$DeployName-backend"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file backend.json \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      S3bucketName=${S3BUCKET} \
      DeployName=${DeployName} \
  --output text
echo "Waiting on ${STACK_NAME} create completion..."
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs



echo "Deploy a CloudFront distribution"
STACK_NAME="$DeployName-distribution"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file distribution.json \
  --parameter-overrides \
      DeployName=${DeployName} \
      HostedZoneId=${HostedZoneId} \
      DomainName=${DomainName} \
      CertificateArn=${CertificateArn} \
  --capabilities CAPABILITY_NAMED_IAM
aws cloudformation wait stack-create-complete --stack-name ${STACK_NAME}
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs
