import boto3
import json
import base64
import uuid

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = "nadialin"
table = dynamodb.Table(TABLE_NAME)

# TBD lambda handle
def handler
    return

# Fecth template for URL
def fetchTemplate( url ):
    return
    
# UeerData json snytax { "userDate": [ {"description": xxx, "base64": "xxx"} ] }
# At aminimum userData[0] is the required steps to setup scoring
# Expected are one or more addiotnal items to define services and/or backdoors
def fetchUserData( url[] ):
    return
    
def fetchServices( url[] ):
    return
    
# Function to put an item into the table
def put_item(item_data):
    if "uuid" not in item_data:
        item_data["uuid"] = str(uuid.uuid4())  # Generate UUID if missing

    table.put_item(Item=item_data)
    print(f"Item inserted: {item_data}")

# Function to get an item from the table
def get_item(uuid, item_type):
    response = table.get_item(Key={"uuid": uuid, "type": item_type})
    return response.get("Item")  # Returns None if not found

if __name__ == "__main__":
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    fetched_item = get_item(uuid, "machine")
    print(f"Fetched Item: {fetched_item}")

    item = {
        "uuid": str(uuid.uuid4()), 
        "type": "instance",
        "machine": uuid,
        "status": "running"
    }
    put_item(item)


"""
# Load instance parameters from JSON file
with open("adam.json", "r") as file:
    instance_params = json.load(file)

# Encode UserData (if present)
if "UserData" in instance_params:
    instance_params["UserData"] = base64.b64encode(instance_params["UserData"].encode("utf-8")).decode("utf-8")

ec2 = boto3.client("ec2", region_name="us-east-2")

# Gt SG and Subnet info
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
