import boto3
import json
import os

DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

def setupScoring():
        # Initialize clients
        lambda_client = boto3.client('lambda')
        eventbridge = boto3.client('events')

        try:
                # Configuration
                rule_name = f"{DEPLOY_NAME}-instanceState"
                rule_description = "Triggers when an EC2 instance changes state"

                event_pattern = {
                        "source": ["aws.ec2"],
                        "detail-type": ["EC2 Instance State-change Notification"],
                        "detail": {
                                "state": ["pending", "running", "stopping", "stopped", "shutting-down", "terminated"]
                        }
                }

                rule_response = eventbridge.put_rule(
                        Name=rule_name,
                        EventPattern=json.dumps(event_pattern),
                        State='ENABLED',
                        Description=rule_description
                )

                rule_arn = rule_response['RuleArn']
                print(f"EventBridge Rule ARN: {rule_arn}")

                # Get Lambda function ARN
                lambda_response = lambda_client.get_function(FunctionName=rule_name)
                lambda_arn = lambda_response['Configuration']['FunctionArn']

                eventbridge.put_targets(
                        Rule=rule_name,
                        Targets=[
                                {
                                    'Id': f"{DEPLOY_NAME}-instanceState",
                                'Arn': lambda_arn
                            }
                        ]
                )

                # Add permissions to allow EventBridge to invoke the Lambda function
                response = lambda_client.get_policy(FunctionName=rule_name)
                policy = json.loads(response['Policy'])

                # Check if the statement ID exists in the policy
                notFound = True
                for statement in policy.get('Statement', []):
                        if statement['Sid'] == statement['Sid']:
                                notFound = False
                if( notFound ):
                        lambda_client.add_permission(
                                FunctionName=rule_name,
                            StatementId='AllowEventBridgeInvoke',
                            Action='lambda:InvokeFunction',
                            Principal='events.amazonaws.com',
                            SourceArn=rule_arn
                        )
                return {
                        "statusCode": 200,
                        "body": "EventBridge rule set to trigger on EC2 state changes."
                }
        except Exception as e:
                return {
                        "statusCode": 500,
                        "body": json.dumps({"error": str(e)})
                }

def lambda_handler(event, context=None):
        # AWS Lambda handler to start event from website
        print("Received event:", json.dumps(event, indent=2))
        query_params = event.get("queryStringParameters", {})
        return( setupScoring() )

if __name__ == "__main__":
        print( setupScoring())