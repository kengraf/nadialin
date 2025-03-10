import sys
import boto3
import json
import os

# Decorator for running test functions
def test(func):
    def wrapper():
        if not callable(func):
            print(f"ℹ️ ({func.__name__}) is not a function")
            return wrapper
        try:
            if func() == True:
                print(f"✅ Passed: {func.__name__}")
            else:
                print(f"❌ Failed: {func.__name__}")
            return wrapper
        except Exception as e:
            print(f"ℹ️ ({func.__name__}) threw exception: {e}")
    return wrapper

           
# --------------------------    

DEPLOY_NAME = os.environ.get("DEPLOY_NAME")
DNS_ROOT=os.environ.get("DNS_ROOT")
DNS_ROOT = f"{DEPLOY_NAME}-{DNS_ROOT}"

# TODO here genrally or in specific tests?
lambda_client = boto3.client('lambda')
db_client = boto3.client('dynamodb')
eventbridge = boto3.client('events')
ec2 = boto3.client('ec2')

@test
def get_env():
    try:
        # Load environment variables from .env file
        with open("../deploy/.env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
                    
        DEPLOY_NAME = os.getenv("DEPLOYNAME")       
        return  DEPLOY_NAME != None
    except Exception as e:
        raise e
    
#--------- Make sure lambdas are available ---------#
@test
def lambdas_installed():
    funcs = [
        'setupScoring',
        'instanceState',
        'doServiceCheck',
        'startScoring',
        'endScoring',
        'eventScores',
        'backupEvent',
        'restoreEvent',
        'databaseItems',
        'runInstances',
        'verifyToken',
        'manageInstance'
        ]
        
    i = len(funcs)
    while i:
        try:
            i -= 1
            response = lambda_client.get_function(FunctionName=f"{DEPLOY_NAME}-{funcs[i]}")
            if funcs[i] in response['Configuration']['FunctionName']:  # Partial match
                funcs.remove(funcs[i])
        except Exception as e:
            pass
   
    if len(funcs):
        for l in funcs:
            print(f"- {DEPLOY_NAME}-{l} not found.")
        return False
    else:
        return True

#--------- Make sure DynamoDB tables are available ---------#
@test
def dynamoDB_tables_installed():
    tables = [
        'event',
        'machines',
        'services',
        'serviceChecks',
        'hackers',
        'squads',
        'instances'
        ]
    try:
        
        paginator = db_client.get_paginator('list_tables')
    
        available = []
        for page in paginator.paginate():
            available.extend(page['TableNames'])
            
        i = len(tables)
        while i:
            i -= 1
            if f"{DEPLOY_NAME}-{tables[i]}" in available:
                tables.remove(tables[i])
    
         
        if len(tables):
            for t in tables:
                print(f"- {DEPLOY_NAME}-{t} not found.")
            return False
        else:
            return True
    except Exception as e:
        print( str(e))
        raise e
# ------------------ LAMBDA functions --------------------------#
@test
def invoke_lambda(function_name, payload={}):
    # Helper function for basic work when testing lambdas
    try:
        response = lambda_client.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',  # Can be 'Event' for async or 'DryRun' for testing
            Payload=json.dumps(payload)  # Convert Python dictionary to JSON string
        )
    
        response_payload = response['Payload'].read().decode('utf-8')
        if response_payload:
            payload = json.loads(response_payload)
            if payload['statusCode'] == 200:
                return True
            print( payload )
        return False
    except Exception as e:
        print( str(e))
        raise e

@test 
def save_backupEvent_data():
    try:
        payload = {} # {"key1": "value1", "key2": "value2"}

        result = invoke_lambda(f"{DEPLOY_NAME}-backupEvent", payload)
        with open("data_backup.json", "w") as json_file:
            json.dump(result, json_file, indent=4)
        return True
    except Exception as e:
        raise e

@test
def renew_setupScoring():
    try:
        payload = {}
        # Remove existing rule
        rule_name = f"{DEPLOY_NAME}-instanceState"
        try:
            response = eventbridge.list_targets_by_rule(Rule=rule_name, 
                                                   EventBusName=event_bus_name)
            targets = response.get("Targets", [])
            target_ids = [target["Id"] for target in targets]
            eventbridge.remove_targets(Rule=rule_name, 
                                  EventBusName=event_bus_name, Ids=target_ids)
            eventbridge.delete_rule(Name=rule_name, EventBusName=event_bus_name)
        except Exception as e:
            pass # Assuming resources not found
        
        result = invoke_lambda(f"{DEPLOY_NAME}-setupScoring", payload)
        
        # Verify rule now exists
        try:
            response = eventbridge.list_targets_by_rule(Rule=rule_name, 
                                                   EventBusName=event_bus_name)
            return True
        except Exception as e:
            print( str(e))
            return False
    except Exception as e:
        raise e

@test
def renew_instanceState():
    try:
        payload = {
            "detail": {
                "instance-id": "i-06a366576ad4d9352",
                "state": "pending"
            }
        }
        
        # Make sure we targeted an active instance
        id = payload['detail']['instance-id']
        try:
            response = ec2.describe_instances( InstanceIds=[id] )          
        except Exception as e:
            print( f"no instance: {id}" )
            return False
        
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        for tag in tags:
            if tag['Key'] == 'Name':
                name = tag['Value']
        m = name.split('-')[0]
        s = name.split('-')[1]          
        ip = response["Reservations"][0]["Instances"][0]["PublicIpAddress"]
        
        # Remove existing rule
        rule_name = f"{DEPLOY_NAME}-doServiceCheck-{name}"
        try:
            rule = eventbridge.describe_rule(Name=rule_name, EventBusName="default")
            response = eventbridge.list_targets_by_rule(Rule=rule_name)
            targets = response.get("Targets", [])
            target_ids = [target["Id"] for target in targets]
            eventbridge.remove_targets(Rule=rule_name, Ids=target_ids)
            eventbridge.delete_rule(Name=rule_name)
        except Exception as e:
            pass # Assuming rule not found
        
        result = invoke_lambda(f"{DEPLOY_NAME}-instanceState", payload)
        
        # Verify rule now exists
        try:
            response = eventbridge.list_targets_by_rule(Rule=rule_name, 
                                                   EventBusName=event_bus_name)
            return True
        except Exception as e:
            print( str(e))
            return False
    except Exception as e:
        raise e

@test
def event_scores():
    try:
        payload = {} # {"key1": "value1", "key2": "value2"}
        print( f"{DEPLOY_NAME}-eventScores" )
        result = invoke_lambda(f"{DEPLOY_NAME}-eventScores", payload)
        print( f"{DEPLOY_NAME}-eventScores" )
        return True
    except Exception as e:
        raise e

@test
def trigger_EventBridge():
    try:
        client = boto3.client('events')
        
        # Define the event to send
        response = client.put_events_EXCEPTION_TODO(
            Entries=[
                {
                  "version": "0",
                  "id": "abcd1234-5678-90ef-ghij-klmnopqrstuv",
                  "detail-type": "EC2 Instance State-change Notification",
                  "source": "custom.myapp",
                  "account": "788715698479",
                  "region": "us-east-2",
                  "resources": ["arn:aws:ec2:us-east-2:788715698479:instance/i-0f5f72f388b78f08e"],
                  "detail": {
                    "instance-id": "i-0f5f72f388b78f08e",
                    "state": "running"
                  }
                }                
            ]
        )
        return response != None
    except Exception as e:
        raise e
    
# ----------------- List of functions to test ------------------#
RUN = True
SKIP = True # Set to True to test all without editing list
tests = [
    ( RUN, get_env ),
    ( SKIP, lambdas_installed ),
    ( SKIP, dynamoDB_tables_installed ),
    ( SKIP, save_backupEvent_data ),
    ( SKIP, renew_setupScoring ),
    ( SKIP, renew_instanceState ),
    ( SKIP, event_scores ),
    ( RUN, trigger_EventBridge )
]
        
for func in tests:
    if func[0]:
        func[1]()
    else:
        print(f"ℹ️ Sipped: ({func[1].__name__})")
        
        

