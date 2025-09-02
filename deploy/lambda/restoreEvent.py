import json
import boto3
import os
from boto3.dynamodb.types import TypeSerializer

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

def json_to_dynamodb(json_data):
        serializer = TypeSerializer()
        return {key: serializer.serialize(value) for key, value in json_data.items()}

def backupEvent(data):
    try:
        tables = {
            "events":None,
            "hunters":None,
            "squads":None,
            "machines":None,
            "instances":None,
            "services":None
        }
        for t in tables.keys():
            try:
                tables[t] = data[t]
                for i in tables[t]:
                    putTableItem(DEPLOY_NAME+'-'+t, json_to_dynamodb(i))
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
    tables_TestData = {
        "events": [
          {
            "startTime": "2025-12-11T00:00:00Z",
          "name": "nadialin"
        }
        ],
          "hunters": [
              {
                "admin": True,
                "squad": "undefined",
                "uuid": "79c58deb-9d26-4ae8-ba46-b445cf985d6b",
                "pictureBytes": "badData",
                "email": "testAdminEmail",
                "sub": "testAdminSid",
                "name": "testAdmin"
            },
              {
                "admin": False,
                "squad": "testSquad",
                "uuid": "79c58deb-9d26-4ae8-ba46-b445cf985d6b",
                "pictureBytes": "badData",
                "email": "testEmail",
                "sub": "testSub",
                "name": "testHunter"
            }              
            ],
          "squads": [
              {
                "name": "testSquad",
                "score": 0
              }
            ],
          "machines": [],
          "instances": [],
          "services": []
        }

    """
    {'events': [{'startTime': {'S': '2017-07-21T17:32:28Z'}, 'homePage': {'S': 'nadialin.kengraf.com'}, 'squadSize': {'N': '1'}, 'endTime': {'S': '2017-07-21T18:32:28Z'}, 'admin': {'S': 'wooba'}, 'name': {'S': 'nadialin'}}], 'hunters': [{'squads': {'S': 'goobas'}, 'admin': {'BOOL': True}, 'email': {'S': 'wooba@gooba.com'}, 'name': {'S': 'wooba'}, 'sub': {'S': 'fakevalue'}}], 'squads': [{'name': {'S': 'goobas'}, 'score': {'N': '0'}}, {'publicKey': {'S': 'fake data'}, 'description': {'S': 'big, furry'}, 'name': {'S': 'bear'}, 'points': {'N': '100'}, 'privateKey': {'S': 'fake data'}}], 'machines': [{'name': {'S': 'nadialin'}, 'templateName': {'S': 'nadialin-base-template'}, 'services': {'L': [{'M': {'name': {'S': 'get_flag'}, 'protocol': {'S': 'http'}, 'expected_return': {'S': '{squad}'}, 'port': {'N': '49855'}, 'url': {'S': 'http://{ip}:49855/flag.txt'}, 'points': {'N': '10'}}}, {'M': {'name': {'S': 'alice_login'}, 'protocol': {'S': 'ssm'}, 'expected_return': {'S': 'alice'}, 'url': {'S': 'alice@{ip}'}, 'points': {'N': '1'}}}]}, 'authorNotes': {'S': 'interesting text'}}], 'instances': [], 'services': []}
    """
    """
    {"event": [], "hunters": [{"email": {"S": "wooba@gooba.com"}, "admin": {"BOOL": True}, "name": {"S": "wooba"}, "sub": {"S": "fakevalue"}, "squads": {"S": "gooba"}}], "squads": [{"name": {"S": "test2"}}, {"name": {"S": "goobas"}, "score": {"N": "0"}}], "machines": [{"name": {"S": "nadialin"}, "templateName": {"S": "nadialin-base-template"}, "services": {"L": [{"M": {"protocol": {"S": "http"}, "port": {"N": "49855"}, "name": {"S": "get_flag"}, "expected_return": {"S": "{squad}"}, "url": {"S": "http://{ip}:49855/{squad}/flag.txt"}, "points": {"N": "1"}}}]}, "authorNotes": {"S": "interesting text"}}], "instances": [], "services": []}
"""

    print( backupEvent(tables_TestData))

