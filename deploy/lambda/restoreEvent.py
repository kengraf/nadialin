import json
import boto3
import os

# Initialize clients
db_client = boto3.client('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

def putTableItem(tableName, item):
    # Add item data to table        
    try:
        response = db_client.put_item(
            TableName=tableName,
            Item=item
        )
        return response
    except Exception as e:
        return str(e)

def backupEvent(data):
    try:
        tables = {
            "event":None,
            "hackers":None,
            "squads":None,
            "machines":None,
            "instances":None,
            "services":None
        }
        for t in tables.keys():
            try:
                tables[t] = data[t]
                for i in tables[t]:
                    putTableItem(DEPLOY_NAME+'-'+t, i)
            except Exception as e:
                # Assume ResourceNotFoundException
                tables[t] = {}
        return tables
    except Exception as e:
        return

def handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    return( backupEvent(event.get('body')) )

if __name__ == "__main__":
    example = {'event': [], 'hackers': [{'email': {'S': 'kengraf57@gmail.com'}, 'uuid': {'S': '0e03c991-aa4d-4455-8473-6bf8f461c910'}}], 'squads': [{'score': {'N': '0'}, 'name': {'S': 'gooba'}}, {'name': {'S': 'wooba'}, 'score': {'N': '16'}}], 'machines': [{'instances': {'L': []}, 'templateName': {'S': 'nadialin-test'}, 'name': {'S': 'nadialin'}, 'services': {'L': [{'S': 'get_flag'}]}, 'authorNotes': {'S': 'interesting things about this machine'}}], 'instances': [{'dns': {'S': 'gooba.nadialin.kengraf.com.'}, 'instanceId': {'S': 'i-07eb00ea906f5fb0d'}, 'ipv4': {'S': '18.223.143.33'}, 'name': {'S': 'nadialin-gooba'}}, {'dns': {'S': 'wooba.nadialin.kengraf.com.'}, 'instanceId': {'S': 'i-0c401009483c83a03'}, 'ipv4': {'S': '18.191.169.135'}, 'name': {'S': 'nadialin-wooba'}}], 'services': [{'port': {'S': '49855'}, 'ipv4': {'S': '18.223.143.33'}, 'action': {'S': 'get_flag'}, 'name': {'S': 'nadialin-gooba'}, 'points': {'N': '1'}}, {'port': {'S': '49855'}, 'ipv4': {'S': '18.191.169.135'}, 'action': {'S': 'get_flag'}, 'name': {'S': 'nadialin-wooba'}, 'points': {'N': '1'}}]}

    print( backupEvent(example))
