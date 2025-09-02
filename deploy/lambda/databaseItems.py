import json
import boto3
import os
import re
from decimal import Decimal
import base64
from boto3.dynamodb.types import TypeDeserializer
from boto3.dynamodb.conditions import Attr

class CustomDeserializer(TypeDeserializer):
    def _deserialize_b(self, value):
        # Keep DynamoDB's base64 string instead of raw bytes
        return base64.b64encode(value).decode("utf-8")  
    def _deserialize_n(self, value):
        return int(value)

# Configuration
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

def dynamodb_to_plain_json(dynamo_item):
    deserializer = CustomDeserializer()
    return {key: deserializer.deserialize(value) for key, value in dynamo_item.items()}

# Lambda to enable REST based action on tables
# URL forms: [GET|PUT|DELETE] http://{domain}/{tableName}/{itemID}
#            GET http://{domain}/{tableName}s
dynamodb = boto3.resource("dynamodb")
REQUEST_HUNTER = {}

# Function to convert Decimal to int 
def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    raise TypeError

def get_all_items(table):
    items = []
    last_evaluated_key = None

    # Loop to handle pagination (DynamoDB returns results in pages)
    while True:
        scan_kwargs = {}
        if last_evaluated_key:
            scan_kwargs["ExclusiveStartKey"] = last_evaluated_key

        response = table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))

        last_evaluated_key = response.get("LastEvaluatedKey")
        if not last_evaluated_key:  # No more pages
            break
    return response["ResponseMetadata"]["HTTPStatusCode"], json.dumps(items, default=convert_decimal)

def get_item(table, item_id):
    response = table.get_item(Key={"name": item_id})
    if "Item" not in response:
        return 404, json.dumps({"error": "Item not found"})
    return response["ResponseMetadata"]["HTTPStatusCode"], json.dumps(response["Item"], default=convert_decimal)
        

def put_item(table, body):
    try:
        if table.name.endswith("squads"):
            # When adding a squad update the hunter
            table_hunter = dynamodb.Table(table.name.replace("squads", "hunters"))
            REQUEST_HUNTER["squad"] = body["name"]
            put_item(table_hunter, REQUEST_HUNTER)
        if REQUEST_HUNTER["admin"] or (table.name.endswith("hunters") and (REQUEST_HUNTER["name"] == body["name"])):
            response = table.put_item(Item=body)
        return response["ResponseMetadata"]["HTTPStatusCode"], ""
    except Exception as e:
        print(e)
        return 400, json.dumps({"error": "Invalid URL format."})

def delete_item(table, item_id):
    response = table.delete_item(Key={"name": item_id})
    return response["ResponseMetadata"]["HTTPStatusCode"], ""

def databaseAction(method, path_parts, body):
    try:
        table_name = path_parts[1]  # Ignore stage "/v1"
        print(f"{method} table:{table_name}")
  
        if table_name.endswith("s"):  # Allow plural GET of all items
            item_id = None
            table_name = "nadialin-"+table_name
        else:
            table_name = "nadialin-"+table_name+"s"
            if (method != "PUT" ):
                item_id = path_parts[2]     # Second part is the ID of item to act on
          
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid URL format."})}
        
    try:
        table = dynamodb.Table(table_name)
        
        if method == "GET":
            if( item_id ):
                return get_item(table, item_id)
            else:
                return get_all_items(table)
        elif method == "PUT":
            return put_item(table, body)
        elif method == "DELETE":
            return delete_item(table, item_id)
        else:
            return {"statusCode": 405, "body": json.dumps({"error": "Method Not Allowed"})}
    
        return tables
    except Exception as e:
        return

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
        table = dynamodb.Table('nadialin-hunters')
        response = table.scan( FilterExpression=Attr("sub").eq(sub))
    except Exception as e:
        raise e
    return response.get('Items', None)[0]
# return dynamodb_to_plain_json(response.get('Items', None)[0])

        
def lambda_handler(event, context):
    print("Received event:", json.dumps(event, indent=2))
    REQUEST_HUNTER = setRequestHunter(event["cookies"])
    
    path_parts = event["requestContext"]["http"]["path"].strip("/").split("/")
    method = event["requestContext"]["http"]["method"]
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = None
    print( f"method:{method} path:{path_parts} body:{body}" )
    return databaseAction( method, path_parts, body )
           
if __name__ == "__main__":
    try:
        cookies = [ os.getenv("COOKIE") ]
        REQUEST_HUNTER = setRequestHunter(cookies)
        path_parts = ["v1", "squad", "gooba" ]
        body = {"name":"wooba", "score":0}
        print( databaseAction( "PUT", path_parts, body )) 
        print( databaseAction( "GET", path_parts, None ))
        body = {"name":"gooba", "score":0}
        print( databaseAction( "PUT", path_parts, body )) 
        path_parts = ["v1", "squads", None ]    
        print( databaseAction( "GET", path_parts, None ))
        path_parts = ["v1", "squad", "gooba" ]    
        print( databaseAction( "DELETE", path_parts, None ))
        path_parts = ["v1", "squad", "wooba" ]    
        print( databaseAction( "DELETE", path_parts, None ))
        print( databaseAction( "GET", path_parts, None ))
        path_parts = ["v1", "squads", None ]    
        print( databaseAction( "GET", path_parts, None ))
    except Exception as e:
        print( str(e) )