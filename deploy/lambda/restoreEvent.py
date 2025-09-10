import json
import boto3
import os

# Initialize clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

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
                tables[t] = data['body'][t]
                for i in tables[t]:
                    table = dynamodb.Table(DEPLOY_NAME+'-'+t)
                    table.put_item( Item=i )                    
            except Exception as e:
                # Assume ResourceNotFoundException
                tables[t] = {}
        return tables
    except Exception as e:
        return

def lambda_handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    # FIX REQUEST_HUNTER needed
    print("Received event:", json.dumps(event, indent=2))
    return( backupEvent(event.get('body')) )

if __name__ == "__main__":
    tables_TestData = {
        "body": {
            "events": [
                { "startTime": "2025-12-11T00:00:00Z", "name": "nadialin" }
            ],
            "hunters": [
                { "admin": True, "squad": "gooba", "uuid": "test-uuid",
                "pictureBytes": "badData", "email": "wooba@gooba.com",
                "sub": "test-sub", "name": "wooba" }
            ],
            "squads": [
                { "name": "gooba","score": 0 }
            ],
            "machines": [
                { "instances":[], "templateName":"nadialin-test", "name":"test",
                  "services":[
                      { 'name': 'get_flag', 'protocol': 'http', 'expected_return': '{squad}',
                        'port': '49855', 'url': 'http://{ip}:49855/flag.txt', 'points': 10    
                        },
                      { 'name': 'wooba_login', 'protocol': 'ssm', 'expected_return': 'wooba',
                        'url': 'wooba@{ip}', 'points': 1
                        }
                      ],
                  "authorNotes":"interesting text"
                }
            ],
            "instances": [],
            "services": []
        }
        }
    print( backupEvent(tables_TestData))

