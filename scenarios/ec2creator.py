import boto3
import json
import base64
import argparse
import requests

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Launch an EC2 instance using parameters from a JSON file.")
parser.add_argument("json_file", help="Path to the JSON file containing EC2 instance parameters.")
args = parser.parse_args()

# Load instance parameters from JSON file
try:
    with open(args.json_file, "r") as file:
        instance_params = json.load(file)
except FileNotFoundError:
    print(f"Error: JSON file '{args.json_file}' not found.")
    exit(1)

# Fetch user-data from URL if "UserDataURL" is provided
if "UserDataURL" in instance_params:
    try:
        response = requests.get(instance_params["UserDataURL"])
        response.raise_for_status()  # Raise an error for bad responses
        user_data = response.text
        print(f"Fetched user-data from {instance_params['UserDataURL']}")
        
        # Encode user-data in Base64
        instance_params["UserData"] = base64.b64encode(user_data.encode("utf-8")).decode("utf-8")

    except requests.RequestException as e:
        print(f"Error fetching UserData: {e}")
        exit(1)

# Remove "UserDataURL" as it's not needed in the API call
instance_params.pop("UserDataURL", None)

# Create EC2 client
ec2 = boto3.client("ec2", region_name="us-east-1")  # Change region if needed

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
