export const handler = async (event) => {

    // Amazon Cognito activates the post-authentication Lambda function after Amazon Cognito signs in a new user.
    // Just a code stump now, expect user attributes to be managed in DynamoDB not Cognito.
    // Docs: https://docs.aws.amazon.com/cognito/latest/developerguide/user-pool-lambda-post-authentication.html
    
    // Dump event data to CloudTrail
    console.log("input = " + JSON.stringify(event) )

    return event;
};
