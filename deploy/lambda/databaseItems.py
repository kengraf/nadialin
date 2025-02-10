import json
import boto3

# Lambda to enable REST based action on tables
# URL forms: [GET|PUT|DELETE] http://{domain}/{tableName}/{itemID}
#            GET http://{domain}/{tableName}s
dynamodb = boto3.resource("dynamodb")

def handler(event, context):
    try:
      print(json.dumps(event))
      http = event["requestContext"]["http"]
      path_parts = http["path"].strip("/").split("/")
  
      table_name = path_parts[1]  # Ignore stage "/v1"
      http_method = http["method"]
      print(f"{http_method} table:{table_name}")

      if table_name.endswith("s"):  # Allow plural GET of all items
        item_id = null
        table_name = "nadialin-"+table_name
      else:
        table_name = "nadialin-"+table_name+"s"
        if (http_method != "PUT" ):
            item_id = path_parts[2]     # Second part is the ID of item to act on
        
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid URL format."})}
      
    table = dynamodb.Table(table_name)

    if http_method == "GET":
        if( item_id ):
          return get_item(table, item_id)
        else:
          return get_all_items(table)
    elif http_method == "PUT":
        body = json.loads(event["body"])
        return put_item(table, body)
    elif http_method == "DELETE":
        return delete_item(table, item_id)
    else:
        return {"statusCode": 405, "body": json.dumps({"error": "Method Not Allowed"})}

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
    return {"statusCode": 200, "body": json.dumps(response["Items"])}

def get_item(table, item_id):
    response = table.get_item(Key={"id": item_id})
    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
    return {"statusCode": 200, "body": json.dumps(response["Item"])}

def put_item(table, body):
    print(f"PUT: {table.table_name} item:{json.dumps(body)}")
    table.put_item(Item=body)
    return {"statusCode": 200, "body": json.dumps({"message": "Item saved", "item": body})}

def delete_item(table, item_id):
    table.delete_item(Key={"id": item_id})
    return {"statusCode": 200, "body": json.dumps({"message": "Item deleted"})}
