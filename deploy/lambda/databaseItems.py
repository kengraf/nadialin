import json
import boto3
from decimal import Decimal

# Lambda to enable REST based action on tables
# URL forms: [GET|PUT|DELETE] http://{domain}/{tableName}/{itemID}
#            GET http://{domain}/{tableName}s
dynamodb = boto3.resource("dynamodb")


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

def get_item(table, key_name, item_id):
    response = table.get_item(Key={key_name: item_id})
    if "Item" not in response:
        return 404, json.dumps({"error": "Item not found"})
    return response["ResponseMetadata"]["HTTPStatusCode"], json.dumps(response["Item"], default=convert_decimal)
        

def put_item(table, body):
    try:
        print(f"put_item body:{body}")
        response = table.put_item(Item=body)
        return response["ResponseMetadata"]["HTTPStatusCode"], ""
    except Exception as e:
        print(e)
        return 400, json.dumps({"error": "Invalid URL format."})

def delete_item(table, kry_name, item_id):
    response = table.delete_item(Key={key_name: item_id})
    return response["ResponseMetadata"]["HTTPStatusCode"], ""

def databaseAction(method, path_parts, body):
    try:
        table_name = path_parts[1]  # Ignore stage "/v1"
        key_name = "sub" if table_name.startswith("hacker") else "name"
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
                return get_item(table, key_name, item_id)
            else:
                return get_all_items(table)
        elif method == "PUT":
            return put_item(table, body)
        elif method == "DELETE":
            return delete_item(table, key_name, item_id)
        else:
            return {"statusCode": 405, "body": json.dumps({"error": "Method Not Allowed"})}
    
        return tables
    except Exception as e:
        return

def lambda_handler(event, context):
    print(json.dumps(event))
    path_parts = event["requestContext"]["http"]["path"].strip("/").split("/")
    method = event["requestContext"]["http"]["method"]
    if "body" in event:
        body = json.loads(event["body"])
    else:
        body = None
    print( f"method:{method} path:{path_parts} body:{body}" )
    return databaseAction( method, path_parts, body )
           
if __name__ == "__main__":
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
