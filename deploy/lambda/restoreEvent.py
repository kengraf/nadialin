import json
import boto3
import os
import re
from boto3.dynamodb.conditions import Attr

# Initialize clients
dynamodb = boto3.resource('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

import boto3
from botocore.exceptions import ClientError

def clearTable(table):

    table_key_names = [key['AttributeName'] for key in table.key_schema]

    scan_kwargs = {
        'ProjectionExpression': ", ".join(f'#{key}' for key in table_key_names),
        'ExpressionAttributeNames': {f'#{key}': key for key in table_key_names}
    }
    
    try:
        with table.batch_writer() as batch:
            while True:
                response = table.scan(**scan_kwargs)
                items = response.get('Items', [])
                
                if not items:
                    break

                for item in items:
                    key = {key_name: item[key_name] for key_name in table_key_names}
                    batch.delete_item(Key=key)
                

                if 'LastEvaluatedKey' in response:
                    scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
                else:
                    break

    except ClientError as e:
        print(f"An error occurred during deletion: {e.response['Error']['Message']}")


def restoreEvent(data):
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
                table = dynamodb.Table(DEPLOY_NAME+'-'+t)
                clearTable(table)
                for i in tables[t]:
                    table.put_item( Item=i )                    
            except Exception as e:
                # Assume ResourceNotFoundException
                tables[t] = {}
        return True
    except Exception as e:
        raise e

def setRequestHunter(cookies):
    try:
        session = [c for c in cookies if c.startswith("session=")]
        print("Session cookie:", session)
        if( len(session) == 0 ):
            return None
        parts = re.split(r"[=:]", session[0])
        if( len(parts) != 3 ):
            return
        sub = parts[1]
        uuid = parts[2]
        table = dynamodb.Table('nadialin-hunters')
        response = table.scan( FilterExpression=Attr("sub").eq(sub))
    except Exception as e:
        raise e
    return response.get('Items', None)[0]

def lambda_handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    global REQUEST_HUNTER
    try:
        print("Received event:", json.dumps(event, indent=2))
        REQUEST_HUNTER = setRequestHunter(event["cookies"])
        
        
        if REQUEST_HUNTER['admin']:
            restoreEvent(event.get('body'))
            print("Restore successful")
            return True
        else:
            raise( Exceoption("Unauthorized"))
    
    except Exception as e:
        print( str(e) )
        return False
        
if __name__ == "__main__":
    try:
        event = {}
        event['cookies'] = [ os.getenv("COOKIE") ]
        
        with open("../../tests/test_event.tmp", "r") as file:
            event['body'] = json.load(file)

        lambda_handler(event, context=None)
    except Exception as e:
        raise e    


