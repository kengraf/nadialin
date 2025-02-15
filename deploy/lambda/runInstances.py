import json
import boto3
import os
import time
import base64
import argparse

# Initialize clients
db_client = boto3.client('dynamodb')
ec2_client = boto3.client('ec2') 
route53_client = boto3.client('route53')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")
DNS_ROOT = os.environ.get("DNS_ROOT", "kengraf.com")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", DEPLOY_NAME+"-machines")

# Single action functions
def fetchSquads():
    try:
        response = db_client.scan(TableName=DEPLOY_NAME+'-squads')
        items = response.get('Items', [])
        
        # If there are more items, keep paginating
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
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
            Key={"name": {"S": machineName}}  # Assuming 'id' is the primary key
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

    # Re-encode in Base64
    encoded_user_data = base64.b64encode(user_data.encode()).decode()
    return encoded_user_data

def runSquadInstance(template, squadUserData,nameTag):
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
        addInstanceItem( nameTag, 
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

def addDNSrecord( squad, id ):
    # Domain name to look up
    try:
        domainName = DNS_ROOT+'.'
        instance_dns = squad + '.' + DEPLOY_NAME + '.' + domainName
        
        # Get hosted zone ID by domain name
        response = route53_client.list_hosted_zones_by_name(DNSName=domainName)
        
        # Find the matching hosted zone
        hostedZoneId = None
        for zone in response['HostedZones']:
            if zone['Name'] == domainName:
                hostedZoneId = zone['Id'].split('/')[-1]  # Extract the ID part
                break
        
        # Get the public IP of the instance
        response = ec2_client.describe_instances(InstanceIds=[id])
        publicIp = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        # Add a DNS record in Route 53
        change_response = route53_client.change_resource_record_sets(
            HostedZoneId=hostedZoneId,
            ChangeBatch={
                'Comment': 'Add A record for EC2 instance',
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': instance_dns,
                            'Type': 'A',
                            'TTL': 300,  # Time to live in seconds
                            'ResourceRecords': [{'Value': publicIp}]
                        }
                    }
                ]
            }
        )
        return (publicIp, instance_dns)

    except Exception as e:
        raise e
 

def updateInstanceTable( name, id, dns, ip ):
    # Push deploy data to DynamoDB machines table
    try:
        # Fetch launch template name from DynamoDB
        response = db_client.put_item(
            TableName=DEPLOY_NAME+'-instances',
            Item={"name": name,
                  "dns": dns,
                  "instanceId": id,
                  "ipv4": ip
                  }
        )
        return response
    except Exception as e:
        raise e
    return

def runInstances(machineName, squadNames):
    try: # No error/null returns, only thrown exceptions

        # Fetch data from DynamoDB
        machine = fetchMachine(machineName)
        template = fetchTemplate( machine["templateName"]["S"] )
        if( squadNames == None ):
            squadNames = fetchSquads()
            
        # Launch everything without waiting
        instanceQueue = {} # Dict of squads, ec2.instance_id
        for s in squadNames:
            squadUserData = customizeTemplate(template,s) 
            id = runSquadInstance(template['LaunchTemplateName'],squadUserData,s) 
            instanceQueue[s] = id
        
        # Set DNS and update DynamoDB when instance is running
        # 10 tries waiting a minute, then abort if not done
        count = 0
        while len(instanceQueue):
            running = {}
            for squad, id in instanceQueue.items():
                if isRunning(id):
                    dns = addDNSrecord( squad, id )
                    updateInstanceTable( machineName+'-'+squad, id, dns[0], dns[1] )
                    running[squad] = id
            for squad in running:
                instanceQueue.pop(squad)            
            count += 1
            time.sleep(60) # 1 minute
            if(count == 10):
                raise( "One or more instance(s) failed to start on time" )
        return {
            "statusCode": 200,
            "body": "All instances are running"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    query_params = event.get("queryStringParameters", {})
    return( runInstances( query_params.get("uuid") ))

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


