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
      aws s3 cp $i.zip s3://${S3BUCKET}/v1/
    done
    cd ..
}

s3() {
    if aws s3api head-bucket --bucket "$S3BUCKET" 2>/dev/null; then
        echo "Bucket '$S3BUCKET' exists."
    else
        echo "Creating bucket '$S3BUCKET'."
        aws cloudformation deploy --stack-name ${DEPLOYNAME}-s3 --template-file s3.yaml \
            --capabilities CAPABILITY_NAMED_IAM --output text \
            --parameter-overrides  S3BUCKET=$S3BUCKET DEPLOYNAME=$DEPLOYNAME \
                DOMAINNAME=$DOMAINNAME
    fi
    
    echo "Uploading website content"
    cd ../website
    aws s3 sync . s3://$S3BUCKET/
    cd ../deploy
    echo "Uploading OpenAPI yaml"
    aws s3 sync . s3://$S3BUCKET/deploy/ --exclude "lambda/*"
}

cf() {
    echo "Deploy CloudFormation(CF) Stack=$DEPLOYNAME..."
    aws cloudformation deploy --stack-name ${DEPLOYNAME} \
      --template-file ${DEPLOYNAME}.yaml --disable-rollback \
      --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
      --force-upload --output text --parameter-overrides \
          S3BUCKET=$S3BUCKET DEPLOYNAME=$DEPLOYNAME DOMAINNAME=$DOMAINNAME \
          HOSTEDZONEID=$HOSTEDZONEID CERTARN=$CERTARN 

    aws cloudformation describe-stacks --stack-name ${DEPLOYNAME} | jq .Stacks[0].Outputs

    echo "Update Gateway CORS settings"
    API_ID = `aws apigatewayv2 get-apis --query "Items[?Name=='nadialin'].ApiId" --output text`

    aws apigatewayv2 update-api --api-id ${API_ID} \
        --cors-configuration '{
            "AllowOrigins": ["https://yourdomain.com"],
            "AllowMethods": ["GET", "POST", "OPTIONS"],
            "AllowHeaders": ["Content-Type"],
            "AllowCredentials": true
            }'

}

test() {
    echo "Executing Test function..."
    # Add testing-related commands here
}

# If no arguments are provided, execute all functions
if [ $# -eq 0 ]; then
    s3
    zips
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
