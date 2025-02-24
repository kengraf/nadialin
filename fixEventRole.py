'''
import boto3

lambda_client = boto3.client("lambda")

def add_lambda_permission(lambda_function_name, rule_arn):
	try:
		response = lambda_client.add_permission(
		    FunctionName=lambda_function_name,
		    StatementId="AllowEventBridgeInvocation",
		    Action="lambda:InvokeFunction",
		    Principal="events.amazonaws.com",
		    SourceArn=rule_arn,
		)
		print("Permission added:", response)
	except lambda_client.exceptions.ClientError as e:
		print(f"Error adding permission: {e}")

# Example usage
add_lambda_permission(
	"nadialin-instanceState",    "arn:aws:events:us-east-2:788715698479:rule/nadialin-instanceState"
)
'''

import boto3
import json

# Initialize AWS clients
logs_client = boto3.client("logs")
iam_client = boto3.client("iam")
events_client = boto3.client("events")

# Configuration
LOG_GROUP_NAME = "/aws/events/EventBridgeLogs"
IAM_ROLE_NAME = "EventBridgeLoggingRole"
EVENT_RULE_NAME = "nadialin-instanceState"
AWS_REGION = "us-east-2"
ACCOUNT_ID = "788715698479"




def create_log_group():
	"""Create CloudWatch Log Group if it does not exist."""
	try:
		logs_client.create_log_group(logGroupName=LOG_GROUP_NAME)
		print(f"✅ Log group {LOG_GROUP_NAME} created.")
	except logs_client.exceptions.ResourceAlreadyExistsException:
		print(f"ℹ️ Log group {LOG_GROUP_NAME} already exists.")
	except Exception as e:
		print(f"❌ Error creating log group: {e}")


def create_iam_role():
	"""Create an IAM role for EventBridge logging if it does not exist."""
	try:
		iam_client.get_role(RoleName=IAM_ROLE_NAME)
		print(f"ℹ️ IAM role {IAM_ROLE_NAME} already exists.")
	except iam_client.exceptions.NoSuchEntityException:
		assume_role_policy = {
		    "Version": "2012-10-17",
		    "Statement": [
		        {
		            "Effect": "Allow",
		            "Principal": {"Service": "events.amazonaws.com"},
		            "Action": "sts:AssumeRole",
		        }
		        ],
		}

		response = iam_client.create_role(
		    RoleName=IAM_ROLE_NAME,
		    AssumeRolePolicyDocument=json.dumps(assume_role_policy),
		)
		print(f"✅ IAM role {IAM_ROLE_NAME} created: {response['Role']['Arn']}")

	# Attach permissions to allow EventBridge to write logs
	policy_document = {
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Effect": "Allow",
	            "Action": ["logs:CreateLogStream", "logs:PutLogEvents"],
	            "Resource": f"arn:aws:logs:{AWS_REGION}:{ACCOUNT_ID}:log-group:{LOG_GROUP_NAME}:*",
	        }
	        ],
	}

	try:
		iam_client.put_role_policy(
		    RoleName=IAM_ROLE_NAME,
		    PolicyName="EventBridgeLoggingPolicy",
		    PolicyDocument=json.dumps(policy_document),
		)
		print("✅ IAM policy attached to role.")
	except Exception as e:
		print(f"❌ Error attaching policy: {e}")


def verify_event_rule():
	"""Verify that the EventBridge rule exists."""
	try:
		response = events_client.describe_rule(Name=EVENT_RULE_NAME)
		print(f"✅ EventBridge rule found: {response['Name']}")
	except events_client.exceptions.ResourceNotFoundException:
		print(f"❌ Error: EventBridge rule {EVENT_RULE_NAME} not found.")
		return False
	return True


if __name__ == "__main__":
	create_log_group()
	create_iam_role()

	if verify_event_rule():
		print("✅ Logging setup complete for EventBridge.")
	else:
		print("❌ Logging setup failed. Check rule existence.")
