import boto3
import json
import base64

# Load instance parameters from JSON file
with open("adam.json", "r") as file:
    instance_params = json.load(file)

# Encode UserData (if present)
if "UserData" in instance_params:
    instance_params["UserData"] = base64.b64encode(instance_params["UserData"].encode("utf-8")).decode("utf-8")

ec2 = boto3.client("ec2", region_name="us-east-2")

# Gt SG and Subnet info
response = ec2.describe_subnets( Filters=[{'Name': 'tag:Name', 'Values': ['nadialinSubnetPublic']}])
subnets = response.get('Subnets', [])
if subnets:
    instance_params["subnetId"] = subnets[0]['SubnetId']
else:
    print("No subnet found")
    exit
    
response = ec2.describe_security_groups( Filters=[{'Name': 'tag:Name', 'Values': ['nadialinSG']}])
sgs = response.get('SecurityGroups', [])
if sgs:
    instance_params["SecurityGroupIds"] = sgs[0]['SecurityGroupId']
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
