import os
import json
import boto3
import uuid
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as Grequests

CLIENT_ID = "1030435771551-qnikf54b4jhlbdmm4bkhst0io28u11s4.apps.googleusercontent.com"

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['TABLE_NAME'] # set by cloudformation

def handler(event, context):
    print(event)
    try:
        # Parse JSON body
        body = json.loads(event["body"])
        token = body.get("idToken")
        
        if not token:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "idToken: is required in body"})
            }
        
        # Call Google service to validate JWT
        idinfo = id_token.verify_oauth2_token(token, Grequests.Request(), CLIENT_ID)
        sub = idinfo['sub']
        email = idinfo['email']
        user_uuid = str(uuid.uuid4())
        name = email.split('@')[0]
        resp = requests.get(idinfo['picture'])
        resp.raise_for_status()
        img_bytes = resp.content        

        # Make first hunter the event admin
        response = dynamodb.scan( TableName=table_name, Select='COUNT' )
        admin = (response["Count"] == 0)
        
        # Update the hunters table
        table = dynamodb.Table(table_name)        
        table.put_item(Item={"name":name, "email": email, 
                             "pictureBytes": img_bytes, "admin" : admin,
                             "sub":sub, "uuid": user_uuid, "squad":"undefined"})

        # TODO/FIX the cookie options
        cookie = f"session={sub}:{user_uuid}; Secure=true; SameSite=Lax; Path=/"
        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json",
                       "Set-Cookie": cookie },
            "body": json.dumps({"message": f"Session created{cookie}"})
        }
    
    except ValueError as e:
        print(f"Error {e}")
        return {
            "statusCode": 401,
            "headers": { "Content-Type": "application/json" },
            "body": f"Error: {e}"
        } 
