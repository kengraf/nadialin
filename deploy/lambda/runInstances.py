import json
import boto3
import os
import time
import base64
import argparse

# Initialize clients
db_client = boto3.client('dynamodb')
ec2_client = boto3.client('ec2') 

# Environment variables
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "LaunchTemplatesTable")
TABLE_KEY = os.environ.get("TABLE_KEY", "default-key")  # Primary key value

def lambda_handler(event, context):
    try:
        # Fetch launch template URL from DynamoDB
        response = dynamodb.get_item(
            TableName=TABLE_NAME,
            Key={"id": {"S": TABLE_KEY}}  # Assuming 'id' is the primary key
        )

        # Check if the item exists
        if "Item" not in response:
            return {"statusCode": 404, "body": json.dumps({"error": "No launch template found"})}

        # Extract launch template URL
        launch_template_url = response["Item"]["url"]["S"]

        # Extract Launch Template ID and Version from the URL (assuming it's structured like this)
        # Example URL format: "https://aws.amazon.com/ec2/launch-template/lt-1234567890abcdef/1"
        lt_id, lt_version = parse_launch_template_url(launch_template_url)

        # Launch EC2 instance using the Launch Template
        instance_response = ec2.run_instances(
            LaunchTemplate={
                "LaunchTemplateId": lt_id,
                "Version": lt_version
            },
            MinCount=1,
            MaxCount=1
        )

        # Get the launched instance ID
        instance_id = instance_response["Instances"][0]["InstanceId"]


def parse_launch_template_url(url):
    """
    Parses a launch template URL and extracts the Launch Template ID and Version.
    Assumes format: https://aws.amazon.com/ec2/launch-template/lt-xxxxxxxxxxxxxxx/version
    """
    parts = url.split('/')
    lt_id = parts[-2]  # Extract Launch Template ID
    lt_version = parts[-1]  # Extract version
    return lt_id, lt_version

# ------------------------------------------------------------
# Initialize EC2 client

# Fetch Launch Template details
template_name = "my-launch-template"
response = ec2_client.describe_launch_template_versions(
    LaunchTemplateName=template_name,
    Versions=['$Latest']
)

# Extract existing UserData
existing_user_data = ""
if 'LaunchTemplateData' in response['LaunchTemplateVersions'][0]:
    if 'UserData' in response['LaunchTemplateVersions'][0]['LaunchTemplateData']:
        existing_user_data = base64.b64decode(
            response['LaunchTemplateVersions'][0]['LaunchTemplateData']['UserData']
        ).decode()

# New script to append
new_script = """\n# Additional user-data script\n
echo "Appending new user data..." >> /tmp/userdata.log
"""

# Combine old and new user-data
updated_user_data = existing_user_data + new_script

# Re-encode in Base64
encoded_user_data = base64.b64encode(updated_user_data.encode()).decode()

# Launch EC2 instance with modified user-data
instance_response = ec2_client.run_instances(
    LaunchTemplate={
        'LaunchTemplateName': template_name,
        'Version': '$Latest'  # Using the latest version of the template
    },
    MinCount=1,
    MaxCount=1,
    UserData=encoded_user_data
)

# Print instance details
instance_id = instance_response['Instances'][0]['InstanceId']
print(f"Instance {instance_id} launched successfully with appended user-data!")

# -------------------------------------------------------------

def runInstances(machineName, squadNames):
    try: # No error/null returns, only thrown exceptions
        instanceQueue = []
        machine = fetchMachine(machineName)
        template = fetchTemplate( machine[templateName] )
        for s in squadNames: # Luanch everything without waiting
            squadTemplate = customizeTemplate(template) # change naming, add squad loign
            instanceQueue.append( runInstance(squadTemplate) )
        count - 0
        while len(instanceQueue):
            for i in instanceQueue:
                if isRunning(i):
                    name = getTagName(i)
                    addDNSrecord( name )
                    updateDatabaseTable( name )
                    instanceQueue.remove(i)
            count += 1
            time.sleep(60) # 1 minute
            if(count == 10)
                raise( "One or more instance(s) failed to start on time" )
        return {
            "statusCode": 200,
            "body": "All instances are running"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

def handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    query_params = event.get("queryStringParameters", {})
    return( runInstances( query_params.get("uuid") ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DynamoDB pull of template to run instances")
    parser.add_argument("--machine", type=str, required=True, help="Machine name")
    parser.add_argument("--squads", type=str, required=True, help="String of squad names")
    args = parser.parse_args()
    print( runInstances( args.machine, args.squads.split() ))


"""

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "nadialin"
table = dynamodb.Table(TABLE_NAME)

# Fecth template for URL
def fetchTemplate( url ):
    return
    
# UeerData json snytax { "userDate": [ {"description": xxx, "base64": "xxx"} ] }
# At aminimum userData[0] is the required steps to setup scoring
# Expected are one or more addiotnal items to define services and/or backdoors
def fetchUserData( url ):
    return
    
def fetchServices( url ):
    return

import boto3

# Function to put an item into the table
def put_item(item_data):
    if "uuid" not in item_data:
        item_data["uuid"] = str(uuid.uuid4())  # Generate UUID if missing

    table.put_item(Item=item_data)
    print(f"Item inserted: {item_data}")

-----------------------------------------------
"""

"""
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Received POST request",
                "received_data": body
            })
        }

    return {
        "statusCode": 405,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Method Not Allowed"})
    }



# Load instance parameters from JSON file
with open("adam.json", "r") as file:
    instance_params = json.load(file)

# Encode UserData (if present)
if "UserData" in instance_params:
    instance_params["UserData"] = base64.b64encode(instance_params["UserData"].encode("utf-8")).decode("utf-8")

ec2 = boto3.client("ec2", region_name="us-east-2")

# Get SG and Subnet info
response = ec2.describe_subnets( Filters=[{'Name': 'tag:Name', 'Values': ['nadialinSubnetPrivate']}])
subnets = response.get('Subnets', [])
if subnets:
    instance_params["SubnetId"] = subnets[0]['SubnetId']
else:
    print("No subnet found")
    exit
    
response = ec2.describe_security_groups( Filters=[{'Name': 'tag:Name', 'Values': ['nadialinSecurityGroup']}])
sgs = response.get('SecurityGroups', [])
if sgs:
    instance_params["SecurityGroupIds"][0] = sgs[0]['GroupId']
else:
    print("No security group found")
    exit
    
try:
    # Launch EC2 instance using parameters from JSON
    response = ec2.run_instances(**instance_params)
    
    # Extract instance details
    instance_id = response["Instances"][0]["InstanceId"]
    print(f"EC2 Instance Launched! Instance ID: {instance_id}")

    # Wait for the instance to be in "running" state
    ec2_resource = boto3.resource("ec2")
    instance = ec2_resource.Instance(instance_id)
    instance.wait_until_running()
    
    # Get Public IP
    instance.load()
    print(f"Instance Public IP: {instance.public_ip_address}")

except Exception as e:
    print(f"Error launching EC2 instance: {e}")
"""
