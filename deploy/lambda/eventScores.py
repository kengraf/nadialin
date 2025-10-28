
import boto3
import json
import argparse
import os
import re
import base64
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from  boto3.dynamodb.types import Binary 

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            # If the Decimal represents a whole number, convert to int
            if obj % 1 == 0:
                return int(obj)
            # Otherwise, convert to float (or handle as needed)
            return float(obj)
        if isinstance(obj, Binary):
            return base64.b64encode(obj.value).decode('utf-8');
        return super(DecimalEncoder, self).default(obj)

# Configuration
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

'''
SQUAD FORMAT NEEDED
{ "squads": [
    {
        "name": "Alice",
        "flag": {
            "name":"Alice", "color":"green", "url":"http://example.com" },
        "score": 28,
        "services": [
            { "name":"get_flag", "color":"green", "url":"http://example.com" },
            {"name":"login_alice", "color":"red", "url":"http://example.com" }
            ]
    }
] }
'''

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def get_all_squads():
    try:
        table = dynamodb.Table(DEPLOY_NAME+'-squads')
        
        squads = []
        response = table.scan()
        
        squads.extend(response.get('Items', []))
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            squads.extend(response.get('Items', []))

        return json.loads(json.dumps(squads, cls=DecimalEncoder))
    except Exception as e:
        raise e

def get_squad_flags(squad):
    try:
        table = dynamodb.Table(DEPLOY_NAME+'-machines')
        return table.get_item( Key={"name": machine } ).get("item")        
    except Exception as e:
        raise e

def get_squad_services(squad):
        try:
            table = dynamodb.Table(DEPLOY_NAME+'-machines')
            return table.get_item( Key={"name": machine } ).get("item")        
        except Exception as e:
            raise e

def eventScores(hunter):
    try:
        # Validate the user
        retVal = { "hunter": hunter }
        retVal["squads"] = get_all_squads()
        return retVal
    except Exception as e:
        raise e
    
def setRequestHunter(cookies):
    try:
        session = [c for c in cookies if c.startswith("session=")]
        if( len(session) == 0 ):
            return None
        parts = re.split(r"[=:]", session[0])
        if( len(parts) != 3 ):
            return None
        sub = parts[1]
        uuid = parts[2] 
        table = dynamodb.Table(DEPLOY_NAME+'-hunters')
        response = table.scan( FilterExpression=Attr("sub").eq(sub)).get('Items')[0]

        if (response != None) and (response["uuid"] == uuid):
            return json.loads(json.dumps(response, cls=DecimalEncoder))
        else:
            raise Exception("Invalid hunter session")  

    except Exception as e:
        raise e
    return {}


def lambda_handler(event, context=None):
    # AWS Lambda targeted from EventBridge
    try:
        print("Received event:", json.dumps(event, indent=2))
        hunter = None
        if "cookies" in event:
            hunter = setRequestHunter(event["cookies"])
        if( hunter ):
            return { "statusCode": 200,"body": json.dumps(eventScores(hunter), indent=2)}
        else:
            return { "statusCode": 302,"body": json.dumps({"exception":"Force authentication"})}
    except Exception as e:
        print("Error:", str(e))
        return {"statusCode": 409, "body": json.dumps({"exception": str(e)})}
        
if __name__ == "__main__":
    try:
        cookie = os.getenv("COOKIE")
        parser = argparse.ArgumentParser(description="Retrieve hunter data and scores")
        parser.add_argument("--cookies", type=str, required=False, help="session cookie", default=cookie)
        args = parser.parse_args()   

        # eventScores raises exception if invalid user
        print( lambda_handler({"cookies": [args.cookies]})["body"] )
        
    except Exception as e:
        print( str(e) )