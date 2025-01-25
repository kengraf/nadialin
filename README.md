# Nadialin

Cloud based "king-of-hill" style cybersecurity practice environment.  
> [!NOTE]
> 'nadialin' is Abenaki for 'the hunter'

### What is "King-of-hill"?
- Everone (teams or individuals) are given access to a system.
- At the start all systems are indentical and insecure.
- The team secures their system and as a by-product understands how to attack other systems.
- A specific file "flag" on the system indicates ownership of that system.
- You want to control the ownership of the flag on as many systems as possible.
- Points are scored by periodic polling of flags on all systems.
- Most points in given time frame wins.

> [!WARNING]
> As of Jan 2025 this repo is once again under active development.  The ultimate goal of this effort is to allow cybersecurity clubs to host staged events.
> __Expect broken items__ 

## High level deployment process
1. In AWS Cloudshell clone this repo: `git clone `
2. Change to the deploy folder: `nadialin/deploy`
3. Set the environment to your values: `nano .env`
4. Run the deployment script: `./deploy.sh`

> [!WARNING]
> THe remainder of thi page is a wokr in progress

## What is needed to run an event?


Substantial AWS infrastructure is needed to support the creation, monitoring, and release of AWS resources.

## This repo focuses on the automation resources using CloudFormation
List of major AWS components
- S3 : GitHub action is used push to a public bucket, TODO: Leverage CloudFront
- Cognito : User management
- API Gateway : Front user interaction with Lambda based features
- VPN : Control user access to scenarios
- Scenario : Templated deployment the machines the user will work with

# UNDER CONSTRUCTION !!!
Currently there are four phases planned
Phase 1: __WIP__ AWS infrastructure (S3, Cognito, DynamoDB, Lambda, API GatewayV2, CloudFront)
Phase 2: __Pending__ VPN (OpenVPN) and RDP server (Guacamole) integration
Phase 3: __Pending__ Scenario infrastructure
Phase 4: __Pending__ Scenario example

### Step 0: Prerequisites
AWS CLI installed; either locally, Cloud Shell, or Cloud9

### Step 1: Clone this repo
Globally replace 'nadialin' with your choosen deploy name.

### Step 2: Enable deployment of repo artifacts to S3
In your GitHub repo settings, add secrets for AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.  
You care about security right?  Best to create a role, user, and access key limited to writing your S3 bucket.  No need to give the Github action extra powers.  
The automated deploy scripts will create an S3 bucket with the deploy name you choose and a random value to make the bucket name globally unique.

### Step 3: Run the deployment script
Argument to the deploy script will propagate the name to all created resources
```
cd ./deploy
./deploy.sh nadialin
```
The result is a set of CloudFormatin stacks with export values 
- nadialin-storage
    - exports: Bucket DomainName and URL
- nadialin-lambda
    - exports: Lambda ARNs
- nadialin-identity  
    - exports: Cognito UserPoolId, UserPoolURL and ClientId
- nadialin-web
    - exports: API Gateway URL, CloudFront URL, and DynamoDB ARN


2. Validate deployment
At this point you should confirm your bucket is populated and publicly flapping in the breeze.



