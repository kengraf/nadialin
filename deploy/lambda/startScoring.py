import boto3
import os
import time
import argparse
import json

# Initialize clients
events_client = boto3.client('events')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

def find_eventbridge_rules(rule_name):
        matching_rules = []

        # Paginate through all rules
        paginator = events_client.get_paginator('list_rules')
        page_iterator = paginator.paginate()

        # Loop through each page of rules
        for page in page_iterator:
                for rule in page['Rules']:
                        # Check if the rule name matches
                        if rule_name in rule['Name']:
                                matching_rules.append(rule)

        return matching_rules

def reset_squads():
        try:
                table = dynamodb.Table(DEPLOY_NAME+'-squads')

                squads = []
                response = table.scan()

                squads.extend(response.get('Items', []))
                while 'LastEvaluatedKey' in response:
                        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                        squads.extend(response.get('Items', []))

                for s in squads:
                        s['score'] = str(0)
                        s['flag'] = s['name']
                        table.put_item( Item=s )
                        
        except Exception as e:
                raise e
        
# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

def startScoring(time):
        # TBD:TODO:BETA time argument ignored
        try: # No error/null returns, only thrown exceptions
                # Squads set flag and scores to ZERO
                reset_squads()
                
                # Enable all EventBridge rules with
                # "{DEPLOY_NAME}-doServiceCheck" as part of its name
                count = 0
                for rule in find_eventbridge_rules(f"{DEPLOY_NAME}-doServiceCheck"):
                        events_client.enable_rule(Name=rule['Name'])
                        count += 1
                return {
                        "statusCode": 200,
                        "body": f"{count} : doServiceCheck rules enabled"
                }
        except Exception as e:
                return {
                        "statusCode": 500,
                        "body": json.dumps({"error": str(e)})
                }

def lambda_handler(event, context=None):
        # AWS Lambda handler for API Gateway v2 (supports only POST)
        print("Received event:", json.dumps(event, indent=2))
        query_params = event.get("queryStringParameters", {})
        return( startScoring( query_params.get("time") ))

if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Take in game action manage machine")
        parser.add_argument("--time", type=str, required=False, help="Local time to turn on scoring, default=now")
        parser.add_argument("--reset", type=str, required=False, help="reset squad scores to zero, default=false")

        args = parser.parse_args()
        if args.reset:
                reset_squads()
        else:
                print( startScoring( args.time ))


