export const handler = async (event) => {

        // Coding stub for actions you only want to provide to authenticated users
        
        // Dump event data to CloudTrail
        console.log("input = " + JSON.stringify(event) );

        var claims = event[ "requestContext" ][ "authorizer" ][ "jwt" ][ "claims" ];
        var group = claims["cognito:groups"];
        var username = claims["cognito:username"];

        const response = {
                statusCode: 200,
                body: JSON.stringify('Authorized as: ' + username + " in group(s): " + group ),
        };
        return response;
      
};