
import boto3
import json
import urllib3
import time
import uuid
import argparse
import os
from datetime import datetime

# Configuration
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

# Initialize DynamoDB client
db_client = boto3.client('dynamodb')

def fetchTableItem(tableName, itemName):
	try:
		response = db_client.get_item(
		    TableName=tableName,
		    Key={"name": {"S": itemName}}
		)

		# Check if the item exists
		if "Item" not in response:
			raise f"{itemName} not found in {tableName}"
		
		return response["Item"]
	except Exception as e:
		raise e

def doFlagCheck( url ):
	try:
		# Make the HTTP request, python server expected to be running in ~
		http = urllib3.PoolManager()
		response = http.request('GET', url)
	
		# Get response text
		data = response.data.decode('utf-8').strip()
		return data
	except Exception as e:
		raise e

def logCheck( serviceName, passed, actual ):
	try:		
		timestamp = str(datetime.now())
	
		# Generate a unique checkId
		check_id = str(uuid.uuid4())
		a = serviceName.split(':')
		action = a[1]
		machine = a[0].split('-')[0]
		squad = a[0].split('-')[1]
	
		db_client.put_item(
			TableName=DEPLOY_NAME+'-serviceChecks',
			Item={
				'id': {'S': check_id },
				'name': {'S': machine},
			    'timestamp': {'S': timestamp },
			    'action': {'S': action },
				'squad': {'S': squad },
				'actual': { 'S': actual },
				'passed': {'BOOL': passed }
			}
		)
	
	except Exception as e:
		print(f"Error: {e}")

def incrementScore( squadName, points ):
	try:		
		squad_table = DEPLOY_NAME+'-squads'
		try:
			old_score = int(fetchTableItem(squad_table, squadName)['score']['N'])
		except Exception as e:
			old_score = 0
			
		db_client.put_item(
			TableName=squad_table,
			Item={
			    'name': {'S': squadName},
				'score': {'N': str(old_score + points)}
			}
		)
	
	except Exception as e:
		print(f"Error: {e}")



def performCheck( checkName ):
	try:
		action = checkName.split(':')[1]
		squad = checkName.split(':')[0].split('-')[1]

		check = fetchTableItem(DEPLOY_NAME+'-services', checkName)
		
		if( action == "get_flag" ): # TODO:BETA Only service currently
			success = False
			actual = doFlagCheck( check['url']['S'] )
			if( squad == actual ):
				success = True
				incrementScore( squad, int(check['points']['N']) )
			logCheck(checkName, success, actual )
			return {
				'statusCode': 200,
				'body': json.dumps({
					'status': 'success',
					'message': f"Scored: {checkName}"
				})
			}
	except Exception as e:
		raise e

def lambda_handler(event, context=None):
	# AWS Lambda targeted from EventBridge
	print(json.dumps(event))
	try:
		checkName = f"{event['machineName']}:{event['serviceName']}"
		print("Received event:", checkName)
		return performCheck( checkName )

	except Exception as e:
		return {"statusCode": 405, 
				"body": json.dumps({"exception": str(e)})
		}
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run service check(s)")
	parser.add_argument("--machine", type=str, required=True, help="Machine name")
	parser.add_argument("--squad", type=str, required=True, help="Squad name")
	parser.add_argument("--check", type=str, required=True, help="Check name")

	args = parser.parse_args()
	print( performCheck( f"{args.machine}-{args.squad}:{args.check}" ))
