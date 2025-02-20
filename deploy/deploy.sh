#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

# Ideally the CloudFormation stacks would be combined into one.
# This appoach allows students to alter steps as needed

STACK_NAME="$DeployName-network"
echo "Creating stack... $STACK_NAME"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file network.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      DeployName=${DeployName} \
  --output text
echo "Waiting on ${STACK_NAME} create completion..."
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs

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
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs

echo "Packaging and uploading the lambda functions"
cd lambda
if [ ! -e "google-package.zip" ]; then
    echo "Add required library to zip."
    mkdir package
    pip install --target ./package google-auth
    pip install --target ./package requests
    cd package/
    zip -r ../google-package.zip .
    cd ..
fi
cp google-package.zip verifyToken.zip
declare -a arr=("backupEvent","databaseItems", "doServiceCheck", "endScoring", "eventScores", "instanceState", "manageInstances", "restoreEvent", "rutimeInstances", "setupScoring", "startScoring", "verifyToken")
for i in "${arr[@]}"
do
  zip $i.zip $i.py
  aws s3 cp $i.zip s3://${S3BUCKET}
done
cd ..

echo "Uploading website content"
cd ../website
aws s3 sync . s3://${S3BUCKET}
cd ../deploy
echo "Uploading OpenAPI yaml"
aws s3 cp apigatewayv2.yaml s3://${S3BUCKET}

echo "Deploying backend components (apigatewayv2, lambda, dynamodb)"
STACK_NAME="$DeployName-backend"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file backend.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
      S3bucketName=${S3BUCKET} \
      DeployName=${DeployName} \
  --output text
echo "Waiting on ${STACK_NAME} create completion..."
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs

echo "Deploy a CloudFront distribution"
STACK_NAME="$DeployName-distribution"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file distribution.yaml \
  --parameter-overrides \
      DeployName=${DeployName} \
      HostedZoneId=${HostedZoneId} \
      DomainName=${DomainName} \
      CertificateArn=${CertificateArn} \
  --capabilities CAPABILITY_NAMED_IAM
aws cloudformation describe-stacks --stack-name ${STACK_NAME} | jq .Stacks[0].Outputs
