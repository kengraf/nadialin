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

dynamodb = boto3.resource('dynamodb')
ec2_client = boto3.client('ec2') 
lambda_client = boto3.client('lambda')
route53_client = boto3.client('route53')
events_client = boto3.client('events')

def deleteScoringEvent(machine, service):
    lambda_name = f"{DEPLOY_NAME}-doServiceCheck"
    rule_name = f"{lambda_name}-{machine}-{service}"

    response = events_client.list_targets_by_rule(Rule=rule_name)
    target_ids = [target['Id'] for target in response.get('Targets', [])]
    if target_ids:
        events_client.remove_targets(Rule=rule_name, Ids=target_ids)    

    response = events_client.delete_rule(
        Name=rule_name,
        Force=True
    )

def addScoringEvent(machine, service):
    # Create the EventBridge rule to fire every minute
    lambda_name = f"{DEPLOY_NAME}-doServiceCheck"
    rule_name = f"{lambda_name}-{machine}-{service}"
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
    try:
        lambda_client.add_permission(
           FunctionName=lambda_name,
           StatementId=f'AllowEventBridgeInvoke-{machine}-{service}',
           Action='lambda:InvokeFunction',
           Principal='events.amazonaws.com',
           SourceArn=rule_arn
        )
    except Exception as e:
        pass
    

def modifyDNSrecord( squad, id, ip, action ):
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
            
        # Add a DNS record in Route 53
        change_response = route53_client.change_resource_record_sets(
            HostedZoneId=hostedZoneId,
            ChangeBatch={
                'Comment': 'UPSERT/DELETE A record for EC2 instance',
                'Changes': [
                    {
                        'Action': action,
                        'ResourceRecordSet': {
                            'Name': instance_dns,
                            'Type': 'A',
                            'TTL': 300,  # Time to live in seconds
                            'ResourceRecords': [{'Value': ip}]
                        }
                    }
                ]
            }
        )
        return (ip, instance_dns)

    except Exception as e:
        raise e
 
def removeServiceItems( machine ):
    try:
        # Load the data needed for the scoring lambda
        table = dynamodb.Table(DEPLOY_NAME+'-machines')
        serviceTable = dynamodb.Table(DEPLOY_NAME+'-services')
        response = table.get_item(
                        Key={"name": machine.split('-')[0]}
                    )
        for sm in response["Item"]["services"]:
            # Retrieve service data
            name = f"{machine}:{sm['name']}"
            
            serviceTable.delete_item(
                Key={"name": name} )
            machine, service = name.split(':')
            deleteScoringEvent( machine, service ) 
        return
    except Exception as e:
        raise e

def addServiceItems( machine, ip ):
    try:
        # Load the data needed for the scoring lambda
        table = dynamodb.Table(DEPLOY_NAME+'-machines')
        response = table.get_item( Key={"name": machine.split('-')[0]} )
        print("addServiceItem")
        print(json.dumps(response))
        
        # Loop through the machine's serviceChecks
        # Generating table entries to support EventBridge rules
        # Unique serviceCheck for each service on a machine
        for s in response["Item"]["services"]:
            # Name is machine-squad:service
            name = s['name']
            s['name'] = f"{machine}:{name}"
            
            # Replace placeholders in URL
            url = s['url']          
            url = url.replace('{ip}', ip )
            url = url.replace('{squad}', machine.split('-')[1] )
            s['url'] = url
            
            # Replace placeholders in the return value
            retVal = s['expected_return']
            s['expected_return'] = retVal.replace('{squad}', machine.split('-')[1] )
            
            # Add new serviceCheck item
            table = dynamodb.Table(DEPLOY_NAME+'-services')
            response = table.put_item( Item=s )

            addScoringEvent(machine, name)
        return
    except Exception as e:
        raise e

def removeInstanceItem( name ):
    # Push the deployment data to instances table
    try:
        table = dynamodb.Table(DEPLOY_NAME+'-instances')
        response = table.delete_item( Key={'name': name} )
        return
    except Exception as e:
        raise e
    return

def addInstanceItem( name, id, ip, dns ):
    # Push the deployment data to instances table
    try:
        table = dynamodb.Table(DEPLOY_NAME+'-instances')
        response = table.put_item( 
            Item={
                "name": name,
                "dns": dns,
                "instanceId": id,
                "status": "running",
                "owner": name.split('-')[1],
                "ipv4": ip 
            }
        )
        return
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
    try:
        # Set DNS, scoring, and update DynamoDB when instance is running
        
        # Get instance data
        response = ec2_client.describe_instances( InstanceIds=[id] )
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']


        # Tag Name determines machine-squad
        name = get_tag(tags)
        machine, squad = name.split('-')

        ip, dns = modifyDNSrecord( squad, id, ip, 'UPSERT' )

        addInstanceItem( name, id, ip, dns )
        
        # The default check is for the ownership flag
        addServiceItems( name, ip )

    except Exception as e:
        print(e)
        raise e
    
def terminateInstance(id):
    try:
        # Unset DNS, scoring, and update DynamoDB when instance terminates

        # Get instance data
        response = ec2_client.describe_instances( InstanceIds=[id] )
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        ip = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        
        # Tag Name determines machine-squad
        name = get_tag(tags)
        machine, squad = name.split('-')
    
        table = dynamodb.Table(DEPLOY_NAME+'-instances')
        table.delete_item( Key={'name': name} )        
             
        # The default check is for the ownership flag
        removeServiceItems( name )

        ip, dns = modifyDNSrecord( squad, id, ip, 'DELETE' )
        
    except Exception as e:
        raise e

def instanceState(id, state):
    try:
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
    except Exception as e:
        raise e
    

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
    print( instanceState( args.instanceId, args.state )['body'])
