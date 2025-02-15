import json
import boto3
import os
import time
import base64
import argparse

# Initialize clients
db_client = boto3.client('dynamodb')
ec2_client = boto3.client('ec2') 
route53_client = boto3.client('route53')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")
DNS_ROOT = os.environ.get("DNS_ROOT", "kengraf.com")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", DEPLOY_NAME+"-machines")

# Single action functions
def fetchTable(tableName):
	try:
		response = db_client.scan(TableName=tableName)
		items = response.get('Items', [])
		
		# If there are more items, keep paginating
		while 'LastEvaluatedKey' in response:
			response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
			items.extend(response.get('Items', []))
		
		return items
	except Exception as e:
		raise e


def backupEvent():
	try:
		tables = {
				'event':None,
				'hackers':None,
				'squads':None,
				'machines':None,
				'instances':None,
				'services':None
			}
		for t in tables.keys():
			try:
				tables[t] = fetchTable(DEPLOY_NAME+'-'+t)
			except Exception as e:
				# Assume ResourceNotFoundException
				tables[t] = {}
		return tables
	except Exception as e:
		return
	
def handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    query_params = event.get("queryStringParameters", {})
    return( backupEvent() )

if __name__ == "__main__":
    print( backupEvent())
