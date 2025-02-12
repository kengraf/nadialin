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

## Phases to running a Nadialin event

### Basic requirements
- AWS account: Only needed for the event admin.  Event participants (hackers) do not need AWS knowledge or access.
- Google OIDC client ID, for event logins
- DNS domain (optional)
### Deploy infrastructure
- Nadialin uses CloudFormation templates to create the required infrastructure: S3, VPC, DynamoDB, IAM, Apigtewayv2, Lambda functions, and CloudFront.
- At idle/unused the infrastructure is free.  It can be deployed well in advance of the event.
### Event configuration
- Determine the (configuration, services, and backdoors) of the instances you will be using in the event.
- Enroll squads and hackers
### Run the event
- Deploy event instances to private subnet
- Deploy OpenVPN server to public subnet
- Replace the waiting page with the home page
- **Have fun!**

## Steps to deploy the infrastructure
1. In an AWS Cloudshell clone this repo: `git clone `
2. Change to the deploy folder: `cd nadialin/deploy`
3. Set the environment to your values: `nano .env`
4. Run the deployment script: `sh deploy.sh`

> [!WARNING]
> THe remainder of this page is a work in progress

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



# OpenID Connect (OIDC)
Using the lessons learned in the previous labs, build out a complete serverless application.

### What the Application does
- Forces a login based on Google ID. (/index.html redirects to /login.html) 
- The OIDC JWT is sent as a POST callback to /verify_token.
- The callback is handled by a lambda function:
  - Generates a UUID
  - Stores the UUIC and OIDC provided email in DynamoDB
  - Redirects back to /index.html
- /index.html displays: OIDC JWT contents, email, and UUID values.

### Components
| CF* | Function | Purpose | Notes |  
| :---: | :---: | :--- | :--- | 
| ❌ | Github | Source (App &IoC) | Clone locally for customization
| ❌ | Google | OIDC provider | Generate client secret; set scopes
| ❌ | CloudFormation | IoC | Need to set custom values
| ✅ | S3 Bucket | Static web content & Lambda packages | Globally unique; user defined name 
| ✅ | Lambda | OIDC callback and session creation | 
| ✅ | DynamoDB | Storage of session UUID | 
| ✅ | API GatewayV2 | Control access to Lambda functions 
| ✅ | Route53 | Provide friendly URL | Optional: requires domain oownership 
| ✅ | CloudFront | CDN for static pages and controls access to ApiGatewayV2 | 

CF*: IoC deployment based on CloudFormation

## Setup (Github, Google, CloudFormation)
### Github
Clone this repo to AWS cloud shell or your local machine.
Optional: Fork this repo to allow for automated workflows and making your work public.
### Google
Follow the Google provided steps to create OAuth 2.0 Client IDs: [LINK](https://developers.google.com/identity/openid-connect/openid-connect)  

> [!IMPORTANT]
> You will need to come back and adjust these settings once the CloudFront URLs are known.

__URIs:__
- The authorized Javascript origin will limit where your client ID can be used.
- The redirect URL will limit where the callback can be redirected to.
- You can have multiple values: (dev, testing, and production)
- Ports matter:  http://localhost and http://localhost:8080 are not the same.

> [!IMPORTANT]
> Edit the lambda function deploy/lambda/verifyToken.py and website/login.html to use your client id.

You can click on the more info button (upper right) to see your client id and secret.
![console capture](images/gcp-console.png)


### CloudFormation
Three (3) CloudFormation templates have been defined.  Storage, Backend, and Distribution.  
A shell script (deploy.sh) has been provided to deploy each of these stacks.  
deploy.sh takes one argument.  A prefix name to be used in naming resources.

> [!TIP]
> Make your prefix name globally unique and lowercase.  This is a S3 limitation.  "it718" is not going to fly.

When a stack deployment completes, one or more URLs will be shown.  You can use these URLs to connect to your S3, Lambda, API, etc.  
Copy the CloudFront URL.  Example: "https://d1mvssppd7zkjp.cloudfront.net"  Go back to the Google Development console and add this as a URI

### S3
The bucket holds the ./website content and the ./deploy/lambda zip package

### Lambda
verifyToken.py handles the OIDC callback, generates a uuid which is stored in DynamoDB, and returns the Google generated JWT.

### DynamoDB
Storage of session uuid, repeated calls are handled as overwrites.

### API GatewayV2
Defines one route /v1/verifyToken.  POST requests that invokes the lambda function.

### Route53 (optional)
Provides custom (friendly) URL to CloudFront.  If you own a domain this is a easier and more predicitable way to setup Google as a OIDC provider.

### CloudFront
Used to cache and serve static files (e.g., HTML, CSS, JavaScript) from an S3 bucket to an origin close to your users for low latency.  It also controls access to the API Gateway: for dynamic requests (e.g., POST, GET, PUT) to your backend services or AWS Lambda.

## Lab Report
Submit to Canvas your login URL.  This is pass/fail based on my login to your site with my Google id.
