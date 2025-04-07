
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

def ssmCheck( check ):
	try:
		# Make the SSM request
		ssm_client = boto3.client("ssm")
		instance_id = 'i-0dc25878f1c0ef3bd'
		# Send command
		response = ssm_client.send_command(
				InstanceIds=[instance_id],
				DocumentName="AWS-RunShellScript",
				Parameters={"commands": ['sshpass -ppasswordsAREwrong ssh alice@172.31.4.95 "whoami"']},
			)
	
		command_id = response["Command"]["CommandId"]
	
		# Wait and fetch output of command
		for _ in range(3):
			response = ssm_client.list_command_invocations(
				CommandId=command_id,
				InstanceId=instance_id,
				Details=True
			)
	
			if response["CommandInvocations"]:
				status = response["CommandInvocations"][0]["Status"]
	
				if status == "Success":
					return response["CommandInvocations"][0]["CommandPlugins"][0].get("Output", "").strip()
				elif status in ["Failed", "TimedOut", "Cancelled"]:
					raise f"Command failed with status: {status}"
	
			time.sleep(1)  # Wait before checking again
	
		raise "SSM command timed out."

	except Exception as e:
		raise f"Error: {e}"


def httpCheck( check ):
	try:
		# Make the HTTP request
		http = urllib3.PoolManager()
		response = http.request('GET', check['url']['S'])
	
		if response.status == 200:
			return response.data.decode('utf-8').strip()
		
		raise Exception(f"Request failed with status: {response.status}")
	except Exception as e:
		raise e

def logCheck( serviceName, actual ):
	try:		
		timestamp = str(datetime.now())
	
		# Generate a unique checkId
		check_id = str(uuid.uuid4())
		instance, action = serviceName.split(':')
		machine, squad = instance.split('-')

	
		db_client.put_item(
			TableName=DEPLOY_NAME+'-serviceChecks',
			Item={
				'id': {'S': check_id },
				'name': {'S': machine},
			    'timestamp': {'S': timestamp },
			    'action': {'S': action },
				'squad': {'S': squad },
				'actual': { 'S': actual }
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
		protocol = check['protocol']['S']
		
		checkFuncs = { 'http':httpCheck, 'ssm':ssmCheck }
		response = checkFuncs[protocol](check)
		
		if( action == "get_flag" ):
			# Reponse is the squad to receive the points
			incrementScore( response, int(check['points']['N']) )
		else:
			if( response == check['expected_return']['S'] ):
				incrementScore( squad, int(check['points']['N']) )
		logCheck(checkName, response )
		return { 'statusCode': 200, 'body': json.dumps({
			'status': 'success', 'message': f"Scored: {checkName}" })
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
