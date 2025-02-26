import boto3
import json

ACCOUNT="788715698479"

# Initialize clients
events_client = boto3.client('events')
lambda_client = boto3.client('lambda')
iam_client = boto3.client('iam')

# Define Rule Name
rule_name = "EC2StateChangeRule"
lambda_function_name = "nadialin-instanceState"

# 1️⃣ Create EventBridge Rule
event_pattern = {
    "source": ["aws.ec2"],
    "detail-type": ["EC2 Instance State-change Notification"],
    "detail": {
        "state": ["running", "stopped", "terminated"]
    }
}

response = events_client.put_rule(
    Name=rule_name,
    EventPattern=json.dumps(event_pattern),
    State="ENABLED",
    Description="Triggers Lambda on EC2 state change"
)
rule_arn = response['RuleArn']
print(f"✅ EventBridge Rule Created: {rule_arn}")

# 2️⃣ Grant EventBridge Permission to Invoke Lambda
lambda_arn = f"arn:aws:lambda:us-east-1:{ACCOUNT}:function:{lambda_function_name}"

lambda_client.add_permission(
    FunctionName=lambda_function_name,
    StatementId=f"EventBridgeInvoke-{rule_name}",
    Action="lambda:InvokeFunction",
    Principal="events.amazonaws.com",
    SourceArn=rule_arn
)
print("✅ Permission granted for EventBridge to invoke Lambda")

# 3️⃣ Add Lambda as Target
events_client.put_targets(
    Rule=rule_name,
    Targets=[
        {
            "Id": "1",
            "Arn": lambda_arn
        }
    ]
)
print("✅ Lambda function added as target")

# 4️⃣ Create IAM Role for CloudWatch Logging (if needed)
role_name = "EventBridgeLoggingRole"
policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

# Check if role exists
try:
    iam_client.get_role(RoleName=role_name)
    print("ℹ️ IAM Role already exists.")
except iam_client.exceptions.NoSuchEntityException:
    # Create role if it doesn't exist
    assume_role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "events.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    iam_client.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(assume_role_policy)
    )
    iam_client.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
    print("✅ IAM Role created and attached for CloudWatch logging")

print("🚀 EventBridge rule setup complete!")
