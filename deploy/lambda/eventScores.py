
import boto3
import json
import argparse
import os
import re

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

def get_hunter_by_sub(sub, uuid):
    try:
        response = dynamodb.scan(TableName=DEPLOY_NAME+'-hunters')
        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = dynamodb.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        for i in items:
            if (sub == i['sub']['S']) and (uuid == i['uuid']['S']):
                return i
            
        raise "Hunter not active/found"
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

def eventScores(hunter):
    try:
        # Validate the user
        retVal = { "hunters": hunter }
        retVal["squads"] = get_all_squads()

        for s in retVal["squads"]:
            services = get_machine_services(DEPLOY_NAME+"-"+s["Squad"])

        return retVal
    except Exception as e:
        raise e
    
def cookieUser(cookies):
    try:
        session = [c for c in cookies if c.startswith("session=")]
        if( len(session) == 0 ):
            return None
        parts = re.split(r"[=:]", session[0])
        if( len(parts) != 3 ):
            return None
        sub = parts[1]
        uuid = parts[2]      
        response = dynamodb.scan(
            TableName='nadialin-hunters',
            FilterExpression='#s = :subVal',
            ExpressionAttributeNames={
                '#s': 'sub'
            },
            ExpressionAttributeValues={
                ':subVal': {'S': sub}
            } 
            )
    except Exception as e:
        raise e
    return response.get('Items', None)[0]

def lambda_handler(event, context=None):
    # AWS Lambda targeted from EventBridge
    try:
        print("Received event:", json.dumps(event, indent=2))
        user = cookieUser(event["cookies"])
        if( user ):
            return { "statusCode": 200,"body": json.dumps(eventScores(user))}
        else:
            return { "statusCode": 302,"body": "Force authentication" }
    except Exception as e:
        return {"statusCode": 409, "body": json.dumps({"exception": str(e)})}
        
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Retrieve hunter data and scores")
        parser.add_argument("--cookies", type=str, required=True, help="session cookie", default="session=sub:uuid")
        args = parser.parse_args()   

        # eventScores raises exception if invalid user
        print( json.dumps(lambda_handler({"cookies": [args.cookies]})) )
        
    except Exception as e:
        print( str(e) )