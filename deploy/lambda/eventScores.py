
import boto3
import json
import argparse
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
        for i in items:
            newSquad = blankSquad
            newSquad['Squad'] = i['name']['S']
            newSquad['Points'] = i['score']['N']
            returnSquad.append(newSquad)
            
        return returnSquad
    except Exception as e:
        raise e

def get_hacker_by_sub(sub, uuid):
    try:
        response = dynamodb.scan(TableName=DEPLOY_NAME+'-hackers')
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        for i in items:
            if (sub == i['sub']['S']) and (uuid == i['uuid']['S']):
                return i
            
        return None
    except Exception as e:
        raise e

def get_machine_services(machine):
    try:
        key = { "name": { 'S': machine }}
        response = dynamodb.get_item(TableName=DEPLOY_NAME+'-machines',Key=key)
        items = response.get('Item', [])

    except Exception as e:
        raise e
    return items

def eventScores(cookie):
    try:
        # Validate the cookie
        sub, uuid = cookie.split(":")
        hacker = get_hacker_by_sub( sub, uuid )
        if( hacker == None):
            return False
        retVal = { "hackers": hacker }
        retVal["squads"] = get_all_squads()

        for s in retVal["squads"]:
            services = get_machine_services(DEPLOY_NAME+"-"+s["Squad"])

        return retVal
    except Exception as e:
        raise e

def lambda_handler(event, context=None):
    # AWS Lambda targeted from EventBridge
    try:
        print("Received event:", json.dumps(event, indent=2))
        session = [c for c in event["cookies"] if c.startswith("session=")]
        key, sub, uuid = session.split("=:")
        return eventScores(sub, uuid)
    except Exception as e:
        return {"statusCode": 405, 
                    "body": json.dumps({"exception": str(e)})}

if __name__ == "__main__":
    cookie = "115804770028255050984:05af9323-481b-4aa1-8612-2439c116dc29"
    parser = argparse.ArgumentParser(description="Retrieve hacker data and scores")
    parser.add_argument("--cookie", type=str, required=True, help="uuid of hacker")
    args = parser.parse_args()   
    print( eventScores(args.cookie) )
