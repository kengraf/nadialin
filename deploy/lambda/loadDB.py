import json
import sys
import argparse
import boto3
import uuid

"""
Load test and/or saved data (JSON) into the DynamoDB database
Invoked via Apigatewayv2 as a POST, or CLI with file argument
"""
def isAdmin(event)
    headers = event.get("headers", {})
    cookies = headers.get("cookie", "")

    # Check that user is an event admin
    return False # Replace with actual validation logic

def load(data):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("nadialin")
    
    for item in data:
    # Ensure 'uuid' exists
    if "uuid" not in item or not item["uuid"]:
        item["uuid"] = str(uuid.uuid4())

    # Ensure 'type' exists
    if "type" not in item or not item["type"]:
        raise ValueError("Missing required attribute: 'type'")

    # Insert into DynamoDB
    response = table.put_item(Item=item)
    print(f"Inserted: {json.dumps(item, indent=2)}")

    return "Data loaded successfully."

    
def handler(event, context=None):
    print("Received event:", json.dumps(event, indent=2))

    if !isAdmin(event):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Unauthorized"})
        }

    data = json.loads(event.get("body", "{}")) if event.get("body") else {}
    result = loadDB( data )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({ "message": result })
    }

def cloudshell_main():
    parser = argparse.ArgumentParser(description="loadDB --data <filename>")
    parser.add_argument("--file", type=str, required=True, help="JSON data")
    
    try:
        args = parser.parse_args()
        with open(args.file, "r") as file:
            data = json.load(file)
        result = loadDB( data )
        print(json.dumps({ "message": result }, indent=2))
    except FileNotFoundError:
        print( f"Error: JSON file '{args.file}' not found.")
      
if __name__ == "__main__":
    if "AWS_EXECUTION_ENV" in sys.environ:  
        # Running inside AWS Lambda (likely triggered by API Gateway)
        def lambda_handler(event, context):
            return handler(event, context)
    else:
        # Running inside CloudShell as CLI
        cloudshell_main()
