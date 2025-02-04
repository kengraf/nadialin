import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource("dynamodb")

def lambda_handler(event, context):
    path_parts = event["path"].strip("/").split("/")
    
    if len(path_parts) < 2:
        return {"statusCode": 400, "body": json.dumps({"error": "Invalid URL format. Expected /{table}/{id}"})}

    table_name = path_parts[0]  # First part is the table name
    item_name = path_parts[1]     # Second part is the item ID

    table = dynamodb.Table(table_name)
    http_method = event["httpMethod"]

    if http_method == "GET":
        return get_item(table, item_name)
    elif http_method == "PUT":
        body = json.loads(event["body"])
        return put_item(table, item_name, body)
    elif http_method == "DELETE":
        return delete_item(table, item_name)
    else:
        return {"statusCode": 405, "body": json.dumps({"error": "Method Not Allowed"})}

def get_item(table, item_name):
    """Retrieve an item from DynamoDB"""
    response = table.get_item(Key={"name": item_name})
    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Item not found"})}
    return {"statusCode": 200, "body": json.dumps(response["Item"])}

def put_item(table, item_name, body):
    """Insert or update an item in DynamoDB"""
    item = {"id": item_name, **body}
    table.put_item(Item=item)
    return {"statusCode": 200, "body": json.dumps({"message": "Item saved", "item": item})}

def delete_item(table, item_name):
    """Delete an item from DynamoDB"""
    table.delete_item(Key={"id": item_name})
    return {"statusCode": 200, "body": json.dumps({"message": "Item deleted"})}
