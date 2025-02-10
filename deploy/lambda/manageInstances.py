import boto3
import json

# Initialize AWS Lambda client
lambda_client = boto3.client('lambda')

def lambda_handler(event, context):
    try:
        response = lambda_client.invoke(
            FunctionName='LambdaB',  # Replace with your actual Lambda B function name
            InvocationType='RequestResponse',  # Use 'Event' for async invocation
            Payload=json.dumps({'key1': 'value1'})  # Replace with the payload you want to send
        )
        
        # Read the response from Lambda B
        response_payload = json.loads(response['Payload'].read())
        
        return {
            'statusCode': 200,
            'body': response_payload
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
