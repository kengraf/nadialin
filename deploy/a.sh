S3BUCKET=nadialin
DeployName=nadialin
STACK_NAME="nadialin-backend"
aws cloudformation deploy --stack-name ${STACK_NAME} \
  --template-file backend.yaml \
   --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
          S3bucketName=${S3BUCKET} \
          DeployName=${DeployName} \
    --output text

