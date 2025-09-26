import sys
import boto3
import json
import os
import requests
import functools

DB_ERROR = False    # True if DB don't exist, or can't backup

# Decorator for running test functions
def test(func):
    @functools.wraps(func)
    def wrapper():
        if DB_ERROR:
            print(f"ℹ️ DB error")
            return wrapper            
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
if (DEPLOY_NAME is None): DEPLOY_NAME = "nadialin"
URL_ROOT = "https://nadialin.kengraf.com" # get_apiEndpoint() will overwrite

# TODO here genrally or in specific tests?
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
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
        'events',
        'machines',
        'services',
        'serviceChecks',
        'hunters',
        'squads',
        'instances'
        ]
    try:
        
        available = dynamodb.tables.all()
        for t in tables:
            table_name = f"{DEPLOY_NAME}-{t}"
            if not any(table.name == table_name for table in available):
                print(f"Table {table_name} not found.")
                return False
        return True
    except Exception as e:
        print( str(e))
        raise e
    
# ------------------ LAMBDA functions --------------------------#
def invoke_lambda(function_name, method="GET", key=None, payload={}):
    # Helper function for basic work when testing lambdas
    try:
        url = f"{URL_ROOT}/v1/{function_name}"
        if( key ): url = f"{url}/{key}"
        headers = {
            "Content-Type": "application/json"
        }
        cookies = {
            "Cookie": os.getenv("COOKIE")
            }
        data = payload
        
        methods = {
            "GET": requests.get,
            "POST": requests.post,
            "PUT": requests.put,
            "DELETE": requests.delete
        }
    
        if method in methods:
            response = methods[method](url, json=payload, cookies=cookies)        
       
        return response.status_code, response.json()
    except Exception as e:
        print( str(e))
        raise e

cookies_TestData = "session=test-sub:test-uuid"

@test 
def putTestData_usingLambda_restoreEvent():
    try:
        status_code, payload  = invoke_lambda("restoreEvent", method="PUT", payload=None)
        return status_code == 200       
    except Exception as e:
        raise e

@test 
def backup_existing_event():
    try:
        status_code, payload = invoke_lambda("backupEvent", method="GET", payload={})
        if status_code != 200:
            return False
        with open("existing_event.tmp", "w") as file:
            json.dump(payload, file, indent=4)
        return True    
    except Exception as e:
        raise e

""" Databases
Hunters: For all hunters(users) name, email, uuid, and squad. Itmes are generated on the hunter's first login.
Machines: Typically a single item, create by admin action. Name, templateName, and Services[]. EC2 instances are tagged with {name)-{squad}. The same EC2 templateName is for all instances. Services is a list of templated JSON objects. "get_flag" is required addtional services can be added. When a instance is created the service template is expanded and added to the services table.
Instances: One item for each running EC2 instance. Created/destroyed with the instance. Item contains: name, DNS name, IP address, and instanceId.
Services: One item per every machine-squad:service combination. Created/destroyed with the instance. Item contains: name, protocol, fully expanded service URL, expected_return, and points.
ServiceChecks: Log of services attempted, Every service, for every machine, once per minute. Does not persist in backupEvent/RestoreEvent cycle.
"""
def database_actions(table, item):
    try:
        status, payload = invoke_lambda(table, "PUT", key="", payload=item)
        if( status != 200 ):
            print( status, payload )
            return False

        status, payload = invoke_lambda(table, "GET", key="gooba", payload=None)
        if( status != 200 ):
            print( status, payload )
            return False

        status, payload = invoke_lambda(table+"s", "GET", key="", payload=None)
        if( status != 200 ):
            print( status, payload )
            return False

        status, payload = invoke_lambda(table, "DELETE", key="gooba", payload=None)
        if( status != 200 ):
            print( status, payload )
            return False

        status, payload = invoke_lambda(table, "GET", key="gooba", payload=None)
        if( status != 200 ):
            print( status, payload )
            return False

        status, payload = invoke_lambda(table+"s", "GET", key="", payload=None)
        if( status != 200 ):
            print( status, payload )
            return False
        return True
    except Exception as e:
        raise e
    
@test
def databaseItems_events():
    try:
        return database_actions("event", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_squads():
    try:
        return database_actions("squad", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_hunters():
    try:
        return database_actions("hunter", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_machines():
    try:
        return database_actions("machine", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_instances():
    try:
        return database_actions("instance", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_services():
    try:
        return database_actions("service", {"name":"gooba","score":0} )
    except Exception as e:
        raise e
    
@test
def databaseItems_serviceChecks():
    try:
        return database_actions("serviceCheck", {"name":"gooba","score":0} )
    except Exception as e:
        raise e

@test
def put_terminateInstances():
    try:
        return False
    except Exception as e:
        raise e


@test
def put_restartInstances():
    try:
        return False
    except Exception as e:
        raise e

@test
def get_instanceWoobaGooba():
    try:
        return False
    except Exception as e:
        raise e

@test
def get_serviceTestWoobaGooba():
    try:
        return False
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
        m, s = name.split('-')         
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
def runInstances():
    try: 
        # find target squad "gooba"
        table = dynamodb.Table(DEPLOY_NAME+'-squads')
        response = table.get_item( Key={"name": "gooba"} )

        if( "Item" not in response ):
            raise Exception("no gooba squad")
        
        # invoke runInstances for gooba
        result = invoke_lambda(f"{DEPLOY_NAME}-runInstance")
        print(result)
        
        # wait for ruuning state
        
        # check that new event bridge rule is available
        
        response = eventbridge.list_rules()
        filtered_rules = [rule for rule in response['Rules'] if "nadialin" in rule['Name']]
        
        for rule in filtered_rules:
            print(f"Name: {rule['Name']}, ARN: {rule['Arn']}, State: {rule['State']}")

        return response != None
    except Exception as e:
        raise e
    
# ----------------- List of functions to test ------------------#
RUN = True
SKIP = False # Set to True to test all without editing list

tests = [
    ( RUN, get_apiEndpoint, True ),
    ( SKIP, lambdas_installed, True ),
    ( SKIP, dynamoDB_tables_installed, True ),
    ( SKIP, backup_existing_event, True ),
    ( SKIP, databaseItems_events, False ),
    ( SKIP, databaseItems_squads, False ),
    ( SKIP, databaseItems_hunters, False ),
    ( SKIP, databaseItems_machines, False ),
    ( SKIP, databaseItems_instances, False ),
    ( SKIP, databaseItems_services, False ),
    ( SKIP, databaseItems_serviceChecks, False ),
    ( RUN, putTestData_usingLambda_restoreEvent, False ),
    ( RUN, runInstances, True ),
    ( SKIP, put_terminateInstances, False ),
    ( SKIP, put_restartInstances, False ),
    ( SKIP, get_instanceWoobaGooba, False ),
    ( SKIP, get_serviceTestWoobaGooba, False ),
    ( SKIP, renew_setupScoring, False ),
    ( SKIP, renew_instanceState, False ),
    ( SKIP, event_scores, False )
]


 

    # Only test if we can do a backup
for func in tests:

    if func[0]:
        passed = func[1]()
        if func[2] and not passed:
            break
    else:
        print(f"ℹ️ Skipped: ({func[1].__name__})")
        
      

