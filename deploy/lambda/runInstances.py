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
GET_FLAG_PORT = os.environ.get("GET_FLAG_PORT", "49855")
TABLE_NAME = DEPLOY_NAME+"-machines"
DNS_ROOT = os.environ.get("DNS_ROOT", "kengraf.com")
SQUAD_LIST='("whale" "kingfisher" "shark" "bear" "porcupine" "eagle" "wolf" "hawk" "squirrel" "falcon")'
SAUCE_LOCATION="https://nadialin.kengraf.com/scripts"

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # If the Decimal represents a whole number, convert to int
            if obj % 1 == 0:
                return int(obj)
            # Otherwise, convert to float (or handle as needed)
            return float(obj)
        if isinstance(obj, Binary):
            return base64.b64encode(obj.value).decode('utf-8');
        return super(DecimalEncoder, self).default(obj)


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
        response = table.get_item( Key={"name": machineName} )
    
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
    user_data = user_data.replace("[[SQUAD_NAME]]", squad)
    user_data = user_data.replace("[[GET_FLAG_PORT]]", GET_FLAG_PORT)
    user_data = user_data.replace("[[SQUAD_LIST]]", SQUAD_LIST)
    user_data = user_data.replace("[[SAUCE_LOCATION]]", SAUCE_LOCATION)

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
        template = fetchTemplate( machine["templateName"] )
        if( squadNames == None ):
            squadNames = fetchSquads()
            
        # Launch everything without waiting.  EventBridge rule activates
        # when instance reaches a running state.  Lambda "instanceState"
        # is called to update dynamoDB tables
        instanceQueue = {} # Dict of squads, ec2.instance_id
        for s in squadNames:
            if isinstance(s, dict):
                s = s['name']            
            squadBasedUserData = customizeTemplate(template,s) 
            id = runSquadInstance(template['LaunchTemplateName'],
                                  squadBasedUserData,machineName+'-'+s) 

        return {
            "statusCode": 200,
            "body": "All instances are launching"
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
    return( runInstances( 
        machineName=query_params.get("machine"),
        squadNames=query_params.get("squads")
    ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DynamoDB pull of template to run instances")
    parser.add_argument("--machine", type=str, required=True, help="Machine name")
    parser.add_argument("--squads", type=str, required=False, help="String of squad names, default is all squads")

    args = parser.parse_args()
    if( args.squads ):
        squads = args.squads.split() 
    else:
        squads = None
    event = {}
    event['queryStringParameters'] = {'machine': args.machine, 'squads': squads }
    print( lambda_handler(event, None) )


