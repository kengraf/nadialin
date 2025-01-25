export const handler = async (event) => {

    // Coding stub for the unauthenticated parts of your deployment
    
    // Dump event data to CloudTrail
    console.log("input = " + JSON.stringify(event) );

    // Echo event back to the user
    const response = {
        statusCode: 200,
        body: JSON.stringify('Not authorized as: ' + username ),
    };
    return response;
};