import json
import boto3
import os
import time
import base64
import argparse

# Initialize clients
db_client = boto3.client('dynamodb')
ec2_client = boto3.client('ec2') 

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")
GET_FLAG_PORT = os.environ.get("GET_FLAG_PORT", "49855")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", DEPLOY_NAME+"-machines")
DNS_ROOT = os.environ.get("DNS_ROOT", "kengraf.com")

# Single action functions
def fetchSquads():
    try:
        response = db_client.scan(TableName=DEPLOY_NAME+'-squads')
        items = response.get('Items', [])
        
        # If there are more items, keep paginating
        while 'LastEvaluatedKey' in response:
            response = db_client.scan(TableName=DEPLOY_NAME+'-squads',
                                      ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        squads = []
        for i in items:
            squads.append(i['name']['S'])
        return squads

    except Exception as e:
        raise e
    
def fetchMachine(machineName):
    try:
        # Fetch launch template name from DynamoDB
        response = db_client.get_item(
            TableName=TABLE_NAME,
            Key={"name": {"S": machineName}}
        )
    
        # Check if the item exists
        if "Item" not in response:
            return {"statusCode": 404, "body": json.dumps({"error": "No launch template found"})}
    
        # Extract launch template URL
        return response["Item"]
    except Exception as e:
        raise e


def fetchTemplate( templateName ):
    # Retrieve the AWS launch template (by name)
    try:
        response = ec2_client.describe_launch_template_versions(
            LaunchTemplateName=templateName,
            Versions=['$Latest']
        )
        return response['LaunchTemplateVersions'][0]
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


def runInstances(machineName, squadNames):
    try: # No error/null returns, only thrown exceptions

        # Fetch data from DynamoDB
        machine = fetchMachine(machineName)
        template = fetchTemplate( machine["templateName"]["S"] )
        if( squadNames == None ):
            squadNames = fetchSquads()
            
        # Launch everything without waiting.  EventBridge rule activates
        # when instance reaches a running state.  Lambda "instanceReady"
        # is called to update dynamoDB tables
        instanceQueue = {} # Dict of squads, ec2.instance_id
        for s in squadNames:
            squadBasedUserData = customizeTemplate(template,s) 
            id = runSquadInstance(template['LaunchTemplateName'],
                                  squadBasedUserData,DEPLOY_NAME+'-'+s) 

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
    return( runInstances( query_params.get("machine") ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DynamoDB pull of template to run instances")
    parser.add_argument("--machine", type=str, required=True, help="Machine name")
    parser.add_argument("--squads", type=str, required=False, help="String of squad names, default is all squads")

    args = parser.parse_args()
    if( args.squads ):
        squads = args.squads.split() 
    else:
        squads = None
    print( runInstances( args.machine, squads ))


