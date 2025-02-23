
import boto3
import json

# Configuration
DEPLOY_NAME = os.environ.get("DEPLOY_NAME", "nadialin")

'''
FORMAT NEEDED
[
    {
        "Squad": "Alice",
        "Flag": {
            "name":"Alice", "color":"green", "url":"http://example.com" },
        "Points": 28,

        "Service status": [
            { "name":"get_flag", "color":"green", "url":"http://example.com" },
            {"name":"login_alice", "color":"red", "url":"http://example.com" }
            ]
    }
]
'''

# Initialize DynamoDB client
dynamodb = boto3.client('dynamodb')

def get_all_squads():
    table = dynamodb.Table(DEPLOY_NAME+'-squads')
    response = table.scan()
    items = response.get('Items', [])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    return items

def get_machine_services(machine):
    table = dynamodb.Table(DEPLOY_NAME+'-services')
    response = table.scan()
    items = response.get('Items', [])

    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))

    return items

def performCheck( checkName ):
	try:
		squads = get_all_squads()
		print(squads)
        
	        if s in squads:
	            services = get_machine_services(DEPLOY_NAME+s[name])
	            print(services)
	            action = checkName.split(':')[1]
	
	except Exception as e:
		raise e

def lambda_handler(event, context=None):
	# AWS Lambda targeted from EventBridge
	print(json.dumps(event))
	try:
		print("Received event:", json.dumps(event, indent=2))
		return eventScores() )
	except Exception as e:
		return {"statusCode": 405, 
				"body": json.dumps({"exception": str(e)})
		}
	

if __name__ == "__main__":
	print( eventScores() )
