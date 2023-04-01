const AWS = require("aws-sdk");

const dynamo = new AWS.DynamoDB.DocumentClient();

const table = "nadialin";

// Positive tests
// Issued in this order will leave the DB unchanged
// curl -v -X "PUT" -H "Content-Type: application/json" -d "{\"data\": \"value\"}" https://<<URL>>/admin/testId
// curl -v https://<URL>/admin
// curl -v -X "PATCH" -H "Content-Type: application/json" -d "{\"data\": \"newValue\"}" https://<<URL>>/admin/testId
// curl -v https://<URL>/admin/testId
// curl -v -X "DELETE" -H "Content-Type: application/json" -d "{\"data\": \"noValue\"}" https://<<URL>>/admin/testId

// No negative tests, and yes lots can go wrong

export const handler = async (event, context) => {
    let body;
    let statusCode = 200;

    // Fill the CloudTrail log
    console.log("event object= " + JSON.stringify(event) );

    var claims = event[ "requestContext" ][ "authorizer" ][ "jwt" ][ "claims" ];
    var group = claims["cognito:groups"];
    var username = claims["cognito:username"];
        
    // Decline access to users not in admin group
    if ( ! group.includes('admin') ) {
        const response = {
            statusCode: 401,
            body: JSON.stringify('Not authorized as: ' + username ),
        };
        return response;   
    };
    
    const headers = {
        "Content-Type": "application/json"
    };

    try {
        switch (event.routeKey) {
            case "DELETE /admin/{id}":
                await dynamo
                    .delete({
                        TableName: table,
                        Key: {
                            id: event.pathParameters.id
                        }
                    })
                    .promise();
                body = `Deleted item ${event.pathParameters.id}`;
                break;
            case "GET /admin/{id}":
                body = await dynamo
                    .get({
                        TableName: table,
                        Key: {
                            id: event.pathParameters.id
                        }
                    })
                    .promise();
                break;
            case "GET /admin":
                body = await dynamo.scan({
                    TableName: table
                }).promise();
                break;
            case "PUT /admin/{id}":
                let requestJSON = JSON.parse(event.body);
                requestJSON.id = event.pathParameters.id;
                await dynamo
                    .put({
                        TableName: table,
                        Item: requestJSON
                    })
                    .promise();
                body = `Put item ${requestJSON.id}`;
                break;
            case "PATCH /admin/{id}":
                const patchJSON = JSON.parse(event.body);
                patchJSON.id = event.pathParameters.id;
                await dynamo
                    .put({
                        TableName: table,
                        Item: patchJSON
                    })
                    .promise();
                body = `Patch item ${patchJSON.id}`;
                break;
            default:
                throw new Error(`Unsupported route: "${JSON.stringify(event)}"`);
        }
    } catch (err) {
        statusCode = 400;
        body = err.message;
    } finally {
        body = JSON.stringify(body);
    }

    return {
        statusCode,
        body,
        headers
    };
};