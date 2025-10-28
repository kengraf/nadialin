
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

# Initialize Boto clients
dynamodb = boto3.resource('dynamodb')
ec2_client = boto3.client('ec2')
ssm_client = boto3.client('ssm')
		
def fetchSquads():
	try:
		table = dynamodb.Table(DEPLOY_NAME+'-squads')

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

		squads = []
		for item in all_items:
			squads.append(item['name'])
		return squads
	except Exception as e:
		raise e

def fetchTableItem(tableName, itemName):
	try:
		table = dynamodb.Table(tableName)
		response = table.get_item( Key={"name": itemName } )
	
		# Check if the item exists
		if response == None or "Item" not in response:
			raise Exception(f"{itemName} not found in {tableName}")
		
		return response["Item"]
	except Exception as e:
		raise e

def fetchInstances(machineName=''):
	try:
		filter = [{'Name': 'instance-state-name', 'Values': ['running']}]
		response = ec2_client.describe_instances(Filters=filter)
		matching_instances = []
		for reservation in response['Reservations']:
			for instance in reservation['Instances']:
				for tag in instance['Tags']:
					if machineName == '' or machineName == tag['Value']:
						matching_instances.append(instance)
						break
		return matching_instances
	except Exception as e:
		print(f"Error finding instance: {e}")
		return []
	
def aptChecks():
	cmdBase = 'source /dev/stdin < <(curl -s https://nadialin.kengraf.com/scripts/test_'
	try:
		instances = fetchInstances()
		squads = fetchSquads()
		results = {}
		
		# Send a command to every instance for every squad
		cmds = []
		for apt in squads:
			results[apt] = {'Red':0, 'Blue':0}
			
			for i in instances:
				id = i['InstanceId']
				for t in i['Tags']:
					if 'nadialin2025' in t['Value']:
						owner = t['Value'].split('-')[1]
						break

				response = ssm_client.send_command(
					InstanceIds=[id],
					DocumentName="AWS-RunShellScript",
					Parameters={"commands": [cmdBase+apt+'.bash)']},
				)
				cmds.append({
					'apt':apt, 
					'cmd_id': response['Command']['CommandId'],
					'owner':owner,
					'instance_id':id
				})
	
		# Need to pause while the commands are registered
		time.sleep(1)
		for c in cmds:
			response = ssm_client.get_command_invocation(
				CommandId=c['cmd_id'],
				InstanceId=c['instance_id']
			)

			if response['Status'] == 'Success':
				results[c['apt']]['Red'] += 1
			else:
				results[c['owner']]['Blue'] += 1
		for s in squads:
			red = results[s]['Red']
			blue = results[s]['Blue']
			setRedBlue( s, red, blue )
			if red == len(squads):
				# Set bonus for all apts still active
				red = len(squads) * 2
			if blue == 0:
				# Set bonus for clean system
				blue = len(squads) * 10
			incrementScore( s, (red+blue)*5)
		print(results)

	except Exception as e:
		raise e
	
def ssmCheck( check ):
	try:
		# Make the SSM request
		machine, action = check['name'].split(':')
		event, owner = machine.split('-')
		squad, testType = action.split('_')
		instance_id = fetchInstances(machine)[0]['InstanceId']

		# Send command
		response = ssm_client.send_command(
			InstanceIds=[instance_id],
			DocumentName="AWS-RunShellScript",
			Parameters={"commands": ["su -c 'ssh -i ~/.ssh/id_rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null wooba@localhost' wooba"]},
			)
		command_id = response['Command']['CommandId']
		print(f"Command ID: {command_id}")
	
		for _ in range(5):
			# Need to pause while the command is registered
			time.sleep(1)
			response = ssm_client.get_command_invocation(
				CommandId=command_id,
				InstanceId=instance_id
			)
			return response['Status'] == "Success"
			
		raise Exception(f"Request failed with status: {response['Status']}")

	except Exception as e:
		raise e


def httpCheck( check ):
	try:
		# Make the HTTP request
		http = urllib3.PoolManager()
		response = http.request('GET', check['url'])
	
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

		table = dynamodb.Table(DEPLOY_NAME+'-serviceChecks')
		new_item = {
			'id': check_id,
			'name': machine,
			'timestamp': timestamp,
			'action': action,
			'squad': squad,
			'actual': actual 
		}
		response = table.put_item(	Item=new_item )
	
	except Exception as e:
		print(f"Error: {e}")

def setRedBlue( squadName, red, blue ):
	try:
		squad_table = DEPLOY_NAME+'-squads'
		item = fetchTableItem(squad_table, squadName)
		item['red'] = str(red)
		item['blue'] = str(blue)
		table = dynamodb.Table(DEPLOY_NAME+'-squads')
		response = table.put_item( Item=item )
		
	except Exception as e:
		print(f"Error: {e}")


def incrementScore( squadName, points ):
	try:		
		squad_table = DEPLOY_NAME+'-squads'
		try:
			item = fetchTableItem(squad_table, squadName)
		except Exception as e:
			raise e
		
		table = dynamodb.Table(squad_table)
		if 'login' not in item: item['login'] = False
		if 'score' not in item: item['score'] = 0
		if item['login']:
			# On one scores when system is "down" for user
			score = int(item['score'])+points
			item['score'] = str(score)
		response = table.put_item( Item=item )
		
	except Exception as e:
		print(f"Error: {e}")



def performCheck( checkName ):
	try:
		instance, action = checkName.split(':')
		machine, squad = instance.split('-')

		check = fetchTableItem(DEPLOY_NAME+'-services', checkName)
				
		if( action == "get_flag" ):
			response = httpCheck(check)
			# Reponse is the squad to receive the points
			incrementScore( response, int(check['points']) )
		elif( action == "wooba_login" ):
			response = ssmCheck(check)
			if( response == True):
				incrementScore( squad, int(check['points']) )
		elif( action == "apt_checks" ):
			response = aptChecks(check)
			# Points for having your APT running
			# Bonus for clearing APT off your squad's instance
		else:
			raise Exception(f"Unknown check type: {action}")	
		
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
	try:
		print( performCheck( f"{args.machine}-{args.squad}:{args.check}" ))
	except Exception as e:
		print(e)
