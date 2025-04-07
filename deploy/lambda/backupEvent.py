import json
import boto3
import os

# Initialize clients
db_client = boto3.client('dynamodb')

# Environment variables
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

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
			"body": tables
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
	print( backupEvent() )

