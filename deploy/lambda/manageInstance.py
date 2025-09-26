import json
import boto3
import os
import time
import base64
import argparse

# Initialize clients
dynamodb = boto3.resource('dynamodb')
ec2_client = boto3.client('ec2') 

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

# Single action functions
def fetchSquads():
    try:
        table = dynamodb.Table(DEPLOY_NAME+'-squads')

        scan_kwargs = {}    
        all_items = []
        
        while True:
            response = table.scan(**scan_kwargs)
            all_items.extend(response.get('Items', []))
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break
            
            # Update the scan parameters for the next iteration
            scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
    
        return json.loads(json.dumps(all_items, cls=DecimalEncoder))

    except Exception as e:
        raise e

def fetchMachine(machineName):
    try:
        # Fetch launch template name from DynamoDB
        table = dynamodb.Table(DEPLOY_NAME+'-machines')
        response = table.get_item( Key={"name": machineName } )

        # Check if the item exists
        if "Item" not in response:
            return {"statusCode": 404, "body": json.dumps({"error": "No launch template found"})}
    
        # Extract launch template URL
        return response["Item"]
    except Exception as e:
        raise e

def customizeTemplate(template,squad):
    # change naming, add squad login
    # return an updated user-data for launch

    existing_user_data = base64.b64decode(
        template['LaunchTemplateData']['UserData']
        ).decode()

    # Ensure flag.txt is set to squad name
    flagText = "echo [[SQUAD]] > /home/[[SQUAD]]/flag.txt"
    user_data = existing_user_data + flagText
    # Correct the "SQUAD_NAME=[[SQUAD]]" construction in template
    user_data = user_data.replace("[[SQUAD]]", squad)
    user_data = user_data.replace("[[GET_FLAG_PORT]]", GET_FLAG_PORT)

    # Re-encode in Base64
    encoded_user_data = base64.b64encode(user_data.encode()).decode()
    return encoded_user_data

def runSquadInstance(template, squadUserData,nameTag):
    # Launch the EC2 for this squad
    try:
        response = ec2_client.run_instances(
            LaunchTemplate={
                'LaunchTemplateName': template,
                'Version': '$Latest'
                },
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                        {'Key': 'Name','Value': nameTag},
                        {'Key': 'Deploy','Value': DEPLOY_NAME}
                    ]
                    }],
            UserData=squadUserData
        )
        return response['Instances'][0]['InstanceId']
    except Exception as e:
        raise e

def isRunning(instanceId):
    # Get instance state
    try:
        response = ec2_client.describe_instances(InstanceIds=[instanceId])
        state = response['Reservations'][0]['Instances'][0]['State']['Name']
        return state == 'running'

    except Exception as e:
        raise e


def manageInstances(machineName, action):
    try: # No error/null returns, only thrown exceptions

        # Fetch data from DynamoDB
        machine = fetchMachine(machineName)

        # Launch everything without waiting.  EventBridge rule activates
        # when instance reaches a running state.  Lambda "instanceReady"
        # is called to update dynamoDB tables
        instanceQueue = {} # Dict of squads, ec2.instance_id
        for s in squadNames:
            squadUserData = customizeTemplate(template,s) 
            id = runSquadInstance(template['LaunchTemplateName'],
                                  squadUserData,machineName+'-'+s) 

        return {
            "statusCode": 200,
            "body": "All instances are running"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def lambda_handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    query_params = event.get("queryStringParameters", {})
    return( manageInstances( query_params.get("machine"),query_params.get("action") ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Take in game action manage machine")
    parser.add_argument("--machine", type=str, required=True, help="Machine name")
    parser.add_argument("--action", type=str, required=True, help="[RESTART, TERMINATE]")

    args = parser.parse_args()
    print( manageInstances( args.machine, args.action )['body'])


