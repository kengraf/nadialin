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

def endScoring(time):
	# TBD:TODO:BETA time argument ignored
	try: # No error/null returns, only thrown exceptions

		# Disable all EventBridge rules with
		# "{DEPLOY_NAME}-doServiceCheck" as part of its name
		rules = find_eventbridge_rules(f"{DEPLOY_NAME}-doServiceCheck")
		
		count = 0
		if rules:
			for rule in rules:
				events_client.disable_rule(Name=rule['Name'])
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
	return( endScoring( query_params.get("time") ))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Take in game action manage machine")
	parser.add_argument("--time", type=str, required=False, help="Local time to turn on scoring, default=now")
	
	args = parser.parse_args()
	print( endScoring( args.time ))


