import boto3
import requests
import time
import uuid
import argparse
from datetime import datetime

# Configuration
DEPLOY_NAME='nadialin'
MACHINE_TABLE = DEPLOY_NAME+'-machines'
INSTANCE_TABLE = DEPLOY_NAME+'-instances'
SQUAD_TABLE = DEPLOY_NAME+'-squads'
SERVICE_TABLE = DEPLOY_NAME+'-services'
SERVICE_CHECKS_TABLE = DEPLOY_NAME+'-serviceChecks'
URL_TO_CHECK = 'http://18.191.33.105:81/flag.txt'

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

def doFlagCheck( machine, squad, ip ):
	try:
		# Make the HTTP request, python server expected to be running in ~
		response = requests.get(f"http://{ip}:4444/flag.txt")
		response.raise_for_status()
	
		# Get response text and timestamp
		response_text = response.text.strip()
		return squad == response_text
	except Exception as e:
		raise e

def logCheck( instanceName, squadName, checkName, passed ):
	try:		
		timestamp = str(datetime.now())
	
		# Generate a unique checkId
		check_id = str(uuid.uuid4())
	
		db_client.put_item(
			TableName=SERVICE_CHECKS_TABLE,
			Item={
				'id': {'S': check_id },
				'name': {'S': checkName},
			    'timestamp': {'S': timestamp },
			    'instance': {'S': instanceName },
				'squad': {'S': squadName},
				'passed': {'BOOL': passed }
			}
		)
	
	except Exception as e:
		print(f"Error: {e}")

def incrementScore( squadName, points ):
	try:		
		old_score = int(fetchTableItem(SQUAD_TABLE, squadName)['score']['N'])
			
		db_client.put_item(
			TableName=SQUAD_TABLE,
			Item={
			    'name': {'S': squadName},
				'score': {'N': str(old_score + points)}
			}
		)
	
	except Exception as e:
		print(f"Error: {e}")



def performCheck( machineName, squadName, serviceName ):
	try:
		instanceName = machineName+'-'+squadName
		instance = fetchTableItem(INSTANCE_TABLE, instanceName)
		ip = instance['ip']['S']
		machine = fetchTableItem(MACHINE_TABLE,machineName)
		services = machine['services']['L']
		
		for s in services:
			if( s['S'] == "get_flag" ): # Only service currently
				success = doFlagCheck( machine, squadName, ip )
				if( success ):
					item = fetchTableItem(SERVICE_TABLE, serviceName)					
					incrementScore( squadName, int(item['points']['N']) )
				logCheck(instanceName, squadName, serviceName, success )
		return 
	except Exception as e:
		raise e

def handler(event, context=None):
	# AWS Lambda handler for API Gateway v2 (supports only POST)
	print("Received event:", json.dumps(event, indent=2))
	query_params = event.get("queryStringParameters", {})
	query_params.get("machine");
	query_params.get("squad");
	query_params.get("service");
	return(performCheck( machines, squads, services ))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Run service check(s)")
	parser.add_argument("--machine", type=str, required=False, help="Machine names, default all")
	parser.add_argument("--squad", type=str, required=False, help="Squad names, default is all squads")
	parser.add_argument("--service", type=str, required=False, help="Service names, default is all squads")

	args = parser.parse_args()
	print( performCheck( args.machine, args.squad, args.service ))
