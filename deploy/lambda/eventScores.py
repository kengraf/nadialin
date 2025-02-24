
import boto3
import json
import os

# Configuration
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

'''
FORMAT NEEDED
[
    {
        "Squad": "Alice",
        "Flag": {
            "name":"Alice", "color":"green", "url":"http://example.com" },
        "Points": 28,

        "Service status": [
            { "name":"get_flag", "color":"green", "url":"http://example.com" },
            {"name":"login_alice", "color":"red", "url":"http://example.com" }
            ]
    }
]
'''

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')
blankService = { "name":"", "color":"", "url":"" }
blankSquad = { "Squad":"", "Flag":{}, "Points":0, "Service status":[]}

def get_all_squads():
    returnSquad = []
    try:
        response = dynamodb.scan(TableName=DEPLOY_NAME+'-squads')
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
    except Exception as e:
        raise e
    for i in items:
        newSquad = blankSquad
        newSquad['Squad'] = i['name']['S']
        newSquad['Points'] = i['score']['N']
        returnSquad.append(newSquad)
        
    return returnSquad

def get_machine_services(machine):
    try:
        key = { "name": { 'S': machine }}
        response = dynamodb.get_item(TableName=DEPLOY_NAME+'-machines',Key=key)
        items = response.get('Item', [])

    except Exception as e:
        raise e
    return items

def eventScores():
    try:
        squads = get_all_squads()
        print(squads)

        for s in squads:
            services = get_machine_services(DEPLOY_NAME+"-"+s["Squad"])
            print(services)

        return squads
    except Exception as e:
        raise e

def lambda_handler(event, context=None):
    # AWS Lambda targeted from EventBridge
    print(json.dumps(event))
    try:
        print("Received event:", json.dumps(event, indent=2))
        return eventScores()
    except Exception as e:
        return {"statusCode": 405, 
                    "body": json.dumps({"exception": str(e)})}

if __name__ == "__main__":
    print( eventScores() )