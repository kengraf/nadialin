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
    tables_TestData = {"event":[],"hackers":[
    {"email":{"S":"wooba@gooba.com"},"uuid":{"S":"0e03c991-aa4d-4455-8473-6bf8f461c910"}}],
    "squads":[{"name":{"S":"wooba"},"score":{"N":"93"}}],
    "machines":[{"instances":{"L":[]},"templateName":{"S":"nadialin-beta"},
    "name":{"S":"nadialin"},"services":{"L":[{"S":"get_flag"}]},
    "authorNotes":{"S":"interesting text"}}],"instances":[]}
    

    print( backupEvent(tables_TestData))

