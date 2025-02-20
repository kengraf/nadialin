import boto3
import json
import logging
import argparse
import os

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")
GET_FLAG_PORT = os.environ.get("GET_FLAG_PORT", "49855")
DNS_ROOT = os.environ.get("DNS_ROOT", "kengraf.com")

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

db_client = boto3.client('dynamodb')
ec2_client = boto3.client('ec2') 
lambda_client = boto3.client('lambda')

def addScoringEvent(machine, service):
    # Create the EventBridge rule to fire every minute
    lambda_name = f"{DEPLOY_NAME}-doServiceCheck"
    rule_name = f"{lambda_name}-{machine}-{service}"
    events_client = boto3.client('events')
    response = events_client.put_rule(
        Name=rule_name,
        ScheduleExpression='rate(1 minute)',
        Tags=[
            {
                'Key': 'Name',
                'Value': rule_name
            },
        ],        
        State='DISABLED'
    )

    rule_arn = response['RuleArn']
    print(f"Rule ARN: {rule_arn}")
    
    # Get Lambda function ARN
    lambda_response = lambda_client.get_function(FunctionName=lambda_name)
    lambda_arn = lambda_response['Configuration']['FunctionArn']
    
    # Add Lambda as the target for the EventBridge rule
    events_client.put_targets(
        Rule=rule_name,
        Targets=[
            {
                'Id': 'Target1',
                'Input': '{"serviceName":"'+service+'","machineName":"'+machine+'"}',
                'Arn': lambda_arn
            }
        ]
    )

    # Add permissions to allow EventBridge to invoke the Lambda function
    lambda_client.add_permission(
        FunctionName=lambda_name,
        StatementId='AllowEventBridgeInvoke',
        Action='lambda:InvokeFunction',
        Principal='events.amazonaws.com',
        SourceArn=rule_arn
    )
    
    

def addDNSrecord( squad, id ):
    # Domain name to look up
    try:
        route53_client = boto3.client('route53')

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
 
def updateServiceTable( machine, ip ):
    try:
        # Load the data needed for the scoring lambda
        tableName = DEPLOY_NAME+'-machines'
        response = db_client.get_item(
                        TableName=tableName,
                        Key={"name": {"S": machine.split('-')[0]}}
                    )
        
        # Loop through the machine's serviceChecks
        # Generating table entries to support EventBridge rules
        # Unique serviceCheck for each service on a machine
        for s in response["Item"]["services"]["L"]['M']:
            # Retrieve service data
            name = s['name']['S']
            points = s['points']['N']
            port = s['port']['N']
            url = s['url']['S']
            protocol = s['protocol']['S']
            retVal = s['expected_return']['S']
            
            tableName = DEPLOY_NAME+'-services'
            url = url.replace('{ip}', ip )
            url = url.replace('{squad}', machine.split('-')[1] )
            retVal = retVal.replace('{squad}', machine.split('-')[1] )
            
            # Add new serviceCheck item
            response = db_client.put_item(
                TableName=DEPLOY_NAME+'-services',
                Item={"name": {'S': machine+':'+ s['S'] },
                      "protocol": {'S': protocol },
                      "url": {'S': url },
                      "points": {'N': points },
                      "port": {'N': port },
                      "expected_return": {'S': retVal }
                      }
            )
            addScoringEvent(machine, s['S'])
        return
    except Exception as e:
        raise e

def updateInstanceTable( name, id, ip, dns ):
    # Push the deployment data to instances table
    try:
        response = db_client.put_item(
            TableName=DEPLOY_NAME+'-instances',
            Item={"name": {'S': name },
                  "dns": {'S': dns },
                  "instanceId": {'S': id },
                  "status": { 'S': "running" },
                  "owner": { 'S': machine.split('-')[1] },
                  "ipv4": {'S': ip }
                  }
        )
        return response
    except Exception as e:
        raise e
    return

def get_tag(tags):
    if not tags: return ''
    for tag in tags:
        if tag['Key'] == 'Name':
            return tag['Value']
    return ''

def ignoreState():
    return

def runningInstance(id):
    # Set DNS, scoring, and update DynamoDB when instance is running

    # Get instance data
    response = ec2_client.describe_instances( InstanceIds=[id] )
    tags = response['Reservations'][0]['Instances'][0]['Tags']
    
    # Tag Name determines machine-squad
    name = get_tag(tags)
    machine = name.split('-')[0]
    squad = name.split('-')[1]

    ip, dns = addDNSrecord( squad, id )
    updateInstanceTable( name, id, ip, dns )
    
    # The default check is for the ownership flag
    updateServiceTable( name, ip )

def terminateInstance(id):
    pass

def instanceState(id, state):
    # Log the instance state change
    logger.info(f"EC2 Instance {id} changed state to {state}")

    stateFuncs = {
        "pending": ignoreState,
        "running": runningInstance,
        "stopping": ignoreState,
        "stopped": ignoreState,
        "shutting-down": ignoreState,
        "terminated": terminateInstance
    }
    stateFuncs[state](id)
    
    # Response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': f"Handled state change for {id} to {state}"
        })
    }

def lambda_handler(event, context):
    # Handle EC2 Instance State-change Notification events from EventBridge.
    print(json.dumps(event))

    # Extract details from the event
    detail = event.get('detail', {})
    instance_id = detail.get('instance-id', 'Unknown')
    state = detail.get('state', 'Unknown')

    try:
        return instanceState( instance_id, state ); 
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="React to instance state change")
    parser.add_argument("--instanceId", type=str, required=True, help="Ec2 instance id")
    parser.add_argument("--state", type=str, required=False, help="New instance state")

    args = parser.parse_args()
    print( instanceState( args.instanceId, args.state ))