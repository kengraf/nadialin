functions (lambda=eventData) R(get) U(put) D(delete)
- event
- squad, hacker
- machine, instance, service, serviceCheck/{machine}(get only)
  
- squadUpdate  ( like many function allow edit of json data to add/delete)

### PRE-EVENT FUNCTIONS  
register running machine  
generating instances create new DB instance table items  

### IN EVENT API FUNCTIONS (lambda=?)
- runInstances
- terminateInstances
- restartInstance/{name}
- getInstanceState/{name}
- validate hacker OIDC token
- generateOvpn/ {name}
- backupEvent : returns JSON
- restoreEvent  data={json}
- getScores

BACKEND FUNCTIONS
- scoreInstance  (gnerate serviceChecks, if live, pull flag, increment squad points)
