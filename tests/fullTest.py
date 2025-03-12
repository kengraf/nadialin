import sys
import boto3
import json
import os
import requests

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
URL_ROOT = "https://nadialin.kengraf.com" # get_apiEndpoint() will overwrite

# TODO here genrally or in specific tests?
lambda_client = boto3.client('lambda')
db_client = boto3.client('dynamodb')
eventbridge = boto3.client('events')
ec2 = boto3.client('ec2')

@test
def get_apiEndpoint():
    global URL_ROOT
    
    try:
        client = boto3.client('apigatewayv2')

        # Get all APIs
        response = client.get_apis()
    
        # Find the API with the matching name
        for api in response.get('Items', []):
            if api.get('Name').lower() == DEPLOY_NAME:
                api_endpoint = api["ApiEndpoint"]
        
                # Construct the full stage URL
                URL_ROOT = f"{api_endpoint}"            
                return True
        return False
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
def invoke_lambda(function_name, method="GET", payload={}):
    # Helper function for basic work when testing lambdas
    try:
        url = f"{URL_ROOT}/v1/{function_name}"
        headers = {
            "Content-Type": "application/json"
        }
        data = payload
        
        methods = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete
        }
    
        if method in methods:
            response = methods[method](url, json=payload)        
       
        return response.status_code, response.text
    except Exception as e:
        print( str(e))
        raise e

tables_TestData = """{"event":[],"hackers":[
{"email":{"S":"wooba@gooba.com"},"uuid":{"S":"0e03c991-aa4d-4455-8473-6bf8f461c910"}}],
"squads":[{"name":{"S":"wooba"},"score":{"N":"93"}}],
"machines":[{"instances":{"L":[]},"templateName":{"S":"nadialin-beta"},
"name":{"S":"nadialin"},"services":{"L":[{"S":"get_flag"}]},
"authorNotes":{"S":"interesting text"}}],"instances":[]}
"""

@test 
def putTestData_usingLambda_restoreEvent():
    try:
        status_code, payload  = invoke_lambda("restoreEvent", method="PUT", payload=tables_TestData)
        return status_code == 200       
    except Exception as e:
        raise e

@test 
def getTestData_usingLambda_backupEvent():
    try:
        status_code, payload = invoke_lambda("backupEvent", method="GET", payload={})
        if status_code != 200:
            return False
        return "".join(payload.split()) == "".join(tables_TestData.split())
     
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
SKIP = False # Set to True to test all without editing list
tests = [
    ( SKIP, get_apiEndpoint ),
    ( SKIP, lambdas_installed ),
    ( SKIP, dynamoDB_tables_installed ),
    ( SKIP, putTestData_usingLambda_restoreEvent ),
    ( RUN, getTestData_usingLambda_backupEvent ),
    ( SKIP, renew_setupScoring ),
    ( SKIP, renew_instanceState ),
    ( SKIP, event_scores ),
    ( RUN, trigger_EventBridge )
]
        
for func in tests:
    if func[0]:
        func[1]()
    else:
        print(f"ℹ️ Skipped: ({func[1].__name__})")
        
        

