curl -X 'PUT' \
	  'https://baje61kzhj.execute-api.us-east-2.amazonaws.com/v1/machine' \
	    -H 'accept: application/json' \
	      -H 'Content-Type: application/json' \
	        -H 'Cookie: session_id=aaa' \
		  -d '{
		    "name": "first",
		      "templateName": "firstone",
		        "authorNotes": "string",
			  "services": [
			      "servicve1"
			        ],
				  "instances": [
				      
				    ]
			    }'
