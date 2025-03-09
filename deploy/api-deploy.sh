export $(grep -v '^#' .env | xargs -I {} echo {} | tr -d '\r')
ApiGatewayRoleArn=$(aws cloudformation list-exports --query "Exports[?Name=='ApiGatewayRoleArn'].Value" --output text)
VerifyTokenFunction=$(aws cloudformation list-exports --query "Exports[?Name=='VerifyTokenFunction'].Value" --output text)
VerifyTokenFunctionArn=$(aws cloudformation list-exports --query "Exports[?Name=='VerifyTokenFunctionArn'].Value" --output text)

echo "Deploy CloudFormation(CF) Stack=$DEPLOYNAME..."
aws cloudformation deploy --stack-name nadialin-api \
  --template-file api.yaml --disable-rollback \
  --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
  --output text --parameter-overrides \
      S3BUCKET=$S3BUCKET DEPLOYNAME=$DEPLOYNAME \
      ApiGatewayRoleArn=$ApiGatewayRoleArn \
      VerifyTokenFunction=$VerifyTokenFunction \
      VerifyTokenFunctionArn=$VerifyTokenFunctionArn \
      EventsExecutionRoleArn=1

aws cloudformation describe-stacks --stack-name ${DEPLOYNAME} | jq .Stacks[0].Outputs

