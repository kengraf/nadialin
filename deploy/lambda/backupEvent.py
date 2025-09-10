import json
import boto3
import os
import base64
from boto3.dynamodb.conditions import Attr
from decimal import Decimal
from  boto3.dynamodb.types import Binary 

class DecimalEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, Decimal):
			# If the Decimal represents a whole number, convert to int
			if obj % 1 == 0:
				return int(obj)
			# Otherwise, convert to float (or handle as needed)
			return float(obj)
		if isinstance(obj, Binary):
			return base64.b64encode(obj.value).decode('utf-8');
		return super(DecimalEncoder, self).default(obj)

# Initialize client (upper level)
dynamodb = boto3.resource('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")


def dynamodb_to_plain_json(dynamo_item):
	deserializer = CustomDeserializer()
	return {key: deserializer.deserialize(value) for key, value in dynamo_item.items()}
			
# Single action functions
def fetchTable(tableName):
	try:
		table = dynamodb.Table(tableName)
	
		scan_kwargs = {}    
		all_items = []
	
		while True:
			response = table.scan(**scan_kwargs)
			all_items.extend(response.get('Items', []))
			last_evaluated_key = response.get('LastEvaluatedKey')
			if not last_evaluated_key:
				break
	
			# Update the scan parameters for the next iteration
			scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
	
		return json.loads(json.dumps(all_items, cls=DecimalEncoder))
	except Exception as e:
		raise e


def backupEvent():
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
				tables[t] = fetchTable(DEPLOY_NAME+'-'+t)
			except Exception as e:
				print(str(e))
				# Assume ResourceNotFoundException
				tables[t] = {}
		return {
			"statusCode": 200,
			"headers": { "Content-Type": "application/json" },
			"body": json.dumps(tables, indent=2)
		}
	except Exception as e:
		print(f"Error {e}")
		return {
			"statusCode": 401,
				"headers": { "Content-Type": "application/json" },
				"body": f"Error: {e}"
		} 

def lambda_handler(event, context=None):
	# AWS Lambda handler for API Gateway v2 (supports only POST)
	print("Received event:", json.dumps(event, indent=2))
	return( backupEvent() )

if __name__ == "__main__":
	print( lambda_handler({})["body"] )

