#!/bin/bash

# Read the deployment variables
export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')

#!/bin/bash

# Define the functions
zips() {
    echo "Packaging and uploading the lambda functions"
    cd lambda
    if [ ! -e "google-package.zip" ]; then
        echo "Add required libraries to verifyToken.zip"
        mkdir package
        pip install --target ./package google-auth
        pip install --target ./package requests
        cd package/
        zip -r ../google-package.zip .
        cd ..
    fi
    cp google-package.zip verifyToken.zip
    
    declare -a arr=("backupEvent" "databaseItems" "doServiceCheck" "endScoring" "eventScores" "instanceState" "manageInstance" "restoreEvent" "runInstances" "setupScoring" "startScoring" "verifyToken")
    for i in "${arr[@]}"
    do
      zip $i.zip $i.py
      aws s3 cp $i.zip s3://${S3BUCKET}
    done
    cd ..
}

s3() {
    echo "Uploading website content"
    cd ../website
    aws s3 sync . s3://${S3BUCKET}
    cd ../deploy
    echo "Uploading OpenAPI yaml"
    aws s3 cp apigatewayv2.yaml s3://${S3BUCKET}  
}

cf() {
    echo "Deploy CloudFormation(CF) Stack=$DEPLOY_NAME..."
    aws cloudformation deploy --stack-name ${DEPLOY_NAME} \
      --template-file ${DEPLOY_NAME}.yaml \
      --capabilities CAPABILITY_NAMED_IAM \
      --parameter-overrides \
          DeployName=${DEPLOY_NAME} \
      --output text
    aws cloudformation describe-stacks --stack-name ${DEPLOY_NAME} | jq .Stacks[0].Outputs
    
}

test() {
    echo "Executing Test function..."
    # Add testing-related commands here
}

# If no arguments are provided, execute all functions
if [ $# -eq 0 ]; then
    zips
    s3
    cf
    tests
else
    # Loop through provided arguments and execute matching functions
    for arg in "$@"; do
        case "$arg" in
            zips) zips ;;
            s3) s3 ;;
            cf) cf ;;
            tests) tests ;;
            *) echo "Invalid argument: $arg" ;;
        esac
    done
fi
