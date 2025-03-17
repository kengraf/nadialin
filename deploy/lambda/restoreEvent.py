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

def lambda_handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    return( backupEvent(event.get('body')) )

if __name__ == "__main__":
    tables_TestData = {"event": [], "hackers": [{"email": {"S": "wooba@gooba.com"}, "admin": {"BOOL": True}, "name": {"S": "wooba"}, "sub": {"S": "fakevalue"}, "squads": {"S": "gooba"}}], "squads": [{"name": {"S": "test2"}}, {"name": {"S": "goobas"}, "score": {"N": "0"}}], "machines": [{"name": {"S": "nadialin"}, "templateName": {"S": "nadialin-base-template"}, "services": {"L": [{"M": {"protocol": {"S": "http"}, "port": {"N": "49855"}, "name": {"S": "get_flag"}, "expected_return": {"S": "{squad}"}, "url": {"S": "http://{ip}:49855/{squad}/flag.txt"}, "points": {"N": "1"}}}]}, "authorNotes": {"S": "interesting text"}}], "instances": [], "services": []}


    print( backupEvent(tables_TestData))

