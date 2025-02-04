import boto3
import json
import base64
import uuid
import argparse

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

def get_latest_ami(region = "us-east-1", platform_name= "al2023-ami-minimal"):
    # Alt platform? "ubuntu-noble-24.04-amd64-pro-server"
    ec2 = boto3.client("ec2", region_name=region)

    images = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "name", "Values": [f"{platform_name}-*"]},
            {"Name": "state", "Values": ["available"]}
        ]
    )

    latest_image = max(images["Images"], key=lambda x: x["CreationDate"])  # Get the newest AMI
    return latest_image["ImageId"]

# Function to put an item into the table
def put_item(item_data):
    if "uuid" not in item_data:
        item_data["uuid"] = str(uuid.uuid4())  # Generate UUID if missing

    table.put_item(Item=item_data)
    print(f"Item inserted: {item_data}")

def runInstance(machineUuid):
    if (machineUuid != "test"):
        machine = table.get_item(Key={"uuid": machineUuid, "type": "machine"}).get('Item', [])
    else:
        # Assume only one machine in databse
        response = dynamodb.scan(
            TableName="nadialin",
            FilterExpression="SortKeyName = :sk",
            ExpressionAttributeValues={
                ":sk": {"S": "machine"}
            }
        )
        machine = response.get('Item', [])
    print(f"Fetched Item: {machine}")

    templateFile = machine.get('templateFile',[])
    # response = s3.get_object(Bucket="nadialin", Key=file_key)
    # content = response["Body"].read().decode("utf-8")
 # Load instance parameters from JSON file
    with open(templateFile, "r") as file:
        params = json.load(file)

    print(f"params={params}")
    params['userData'] = ""
    for u in machine.get('userData',[]):
        with open(u, "r") as file:
            j = json.load(file)
            print(f"j={j}")
            uData = j['userData']
            print(f"userData={uData}")
            params['userData'] +=  uData
    for s in machine.get('services',[]):
            print(f"service={s}")
        
    item = {
        "uuid": str(uuid.uuid4()), 
        "type": "instance",
        "machine": machineUuid,
        "status": "running"
    }
    put_item(item)

def handler(event, context=None):
    # AWS Lambda handler for API Gateway v2 (supports only POST)
    print("Received event:", json.dumps(event, indent=2))
    query_params = event.get("queryStringParameters", {})
    return( runInstance( query_params.get("uuid") ))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DynamoDB pull of template to run instances")
    parser.add_argument("--uuid", type=str, required=True, help="UUID of machine record")
    args = parser.parse_args()
    print( runInstance( args.uuid ))
        
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
