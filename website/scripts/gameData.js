
createGame = (json) => {
    if (json.email === undefined) { return null; }
    if (json.scenario === undefined) { return null; }
    if (json.budget === undefined) { return null; }
    if (json.footer === undefined) { return null; }
    return json
}

validId = (j, id) => {
  for (x in j) {
    if (j[x].id == id) {
      return true;
    }
  }
  // JSON is flawed, TBD, really sure help user with a message
  console.log("Unknown id: " + id );
  return false;
}

validDetections = (j,d) => {
  for (x in d) {
      id = d[x].split(".")[0];
      if(validId(j,id) == false ) { console.log("Unknown detection: " + d[x] ); return false; }
  }

}

validateGameLinks = (j) => {
  for (x in j.scenarios) {
    for (y in j.scenarios[x].compromises) {
      id = j.scenarios[x].compromises[y];
      if(validId(j.compromises,id) == false ) { console.log("Unknown compromise: " + id ); return false; }
    }
    for (y in j.scenarios[x].escalations) {
      id = j.scenarios[x].escalations[y];
      if(validId(j.escalations,id) == false ) { console.log("Unknown escalations: " + id ); return false; }
    }
    for (y in j.scenarios[x].presistences) {
      id = j.scenarios[x].presistences[y];
      if(validId(j.presistences,id) == false ) { console.log("Unknown presistences: " + id ); return false; }
    }
    for (y in j.scenarios[x].exfils) {
      id = j.scenarios[x].exfils[y];
      if(validId(j.exfils,id) == false ) { console.log("Unknown exfils: " + id ); return false; }
    }
  }
  for (x in j.compromises) {
    if( validDetections(j.procedures, j.compromises[x].detections) == false) { return false; }
  }
  for (x in j.escalations) {
    if( validDetections(j.procedures, j.escalations[x].detections) == false) { return false; }
  }
  for (x in j.presistences) {
    if( validDetections(j.procedures, j.presistences[x].detections) == false) { return false; }
  }
  for (x in j.exfils) {
    if( validDetections(j.procedures, j.exfils[x].detections) == false) { return false; }
  }
  for (x in j.procedures ) {
    for (y in j.procedures[x].requirements) {
      id = j.procedures[x].requirements[y];
      if(validId(j.procedures,id) == false ) { return false; }
    }
  }

  return true;
}