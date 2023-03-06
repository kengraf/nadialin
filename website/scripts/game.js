/*global Wlowi _config*/

var Wlowi = window.Wlowi || {};

// TODO get rid of all the TODOs
var todo = true;

// Globals to run game play
var GD = {};	    // Game Data: presisted as JSON object
var cardQueue =	[]; // Attack objects waiting for user to run, {phase,title,html,type,action}
var actionQueue	= [];	// Attacks, bypasses, injects waiting to be shown
var alertsComplete = false; // Signal to stop processing modals

const colors = {"unavailable": "#111111", "off": "#0074D9",
		"on": "#2ECC40", "compromised":"#9B870C", "broken":"#FF4136",
		"black": "#111111", "blue":"#0074D9", "red":"#FF4136", "green":"#2ECC40", "yellow":"#FFDC00"};

function runDefense () {
    // Invoked when the player clicks the "RUN DEFENSE" button
    alertsComplete = false;
    
    cardQueue.forEach(function (c) {
	// Cycle through the queue: attacks, bypasses, injects

	switch(c.type) {
	  case "technique":
	    // eval against deployed mitigations
	    
	    if( GD.attackStatus < c.phase ) {
		// Ignore card as proper phase not reached
		break;
	    }
	    
	    // Ingore technique if mitigation is deployed
	    var blocked = false;
	    var needed = mitreAttack.relationships.filter(o => o.technique === c.id);
	    needed.forEach( function(n) {
		var m = mitreAttack.mitigations.find(o => o.id === n.mitigation);
		if( m.inplay === true ) {
		    if( m.state === 'on' ) {
			// Proper mitigation card deployed
			blocked = true;
		    }
		}
	    });
	    if( blocked ) {
		// Mitigation is in place
		break;
	    }
	    
	    
	    // The technique worked, so flow through to bypass
 	    
	  case "bypass":
	    // Escalate attack status
	    GD.attackStatus = c.phase +1;

	  case "inject":
	    // show modal for attack action is taken by modal button
	    actionQueue.push(c);
	}
    });
    cardQueue = [];
    showIncidentModal();
}

function handleEvent(e) {
    alert( "Game request failed" );
}

function addListeners(xhr) {
    xhr.addEventListener('error', handleEvent);
}
    
// Modal functions
const gameIdtext = [
    '<div class="input-group mb-3"> <div class="input-group-prepend">',
    '<span class="input-group-text" id="basic-addon1">Game ID</span></div>',
    '<input type="text" id="gameModalID" class="form-control" placeholder="Enter your game ID"',
    ' aria-label="GameId" aria-describedby="basic-addon1"></div>',
    ].join("\n");
    
function loadGameModal () {
    var m = jQuery('#cardModal');
    m.find('.modal-title').text("Load Game State");
    m.find('.modal-body').html( gameIdtext );
    m.find('.modal-footer').html( '<button class="btn btn-default btn-primary" id="gameModalAction">Load Game</button>');
    jQuery('#gameModalAction').on('click', function(event) {
	loadGame();
    });
    m.modal('show');
}

function saveGameModal () {
    var m = jQuery('#cardModal');
    m.find('.modal-title').text("Save Game State");
    m.find('.modal-body').html( gameIdtext );
    m.find('.modal-footer').html( '<button class="btn btn-default btn-primary" id="gameModalAction">Save Game</button>');
    jQuery('#gameModalAction').on('click', function(event) {
	saveGame();
    });
    m.modal('show');

}

function showWinnerModal () {
    showModal("WINNER!", "Congratulations","");
}

function showSuccessModal () {
    showModal("SUCCESS", "The level has been successfully defended.<br>Ready for a tougher challenge?","");
}

function showGameOverModal () {
    document.getElementById("game").style.background = '#000000';
    showModal("Game Over", "Well has least no one got hurt.  Try again.","");
}

function showModal (title, html, footer) {
    var m = jQuery('#cardModal');
    m.find('.modal-title').text(title);
    m.find('.modal-body').html(html);
    m.find('.modal-footer').html(footer);
    m.modal('show');
}

function showIncidentModal () {
    if( alertsComplete === true ) {
	return false;
    }
    
    // Use the budget number from current modal before moving the queue
    var m = jQuery('#cardModal');

    // show modal for attack action is taken by modal button
    var a = actionQueue.pop();
    if( a != undefined ) {
	// Modal dismiss actions will recursively callback to this function
	showAlert(a);
    } else {
	// Queue empty, did we win?
	alertsComplete = true;
	
	if( GD.budget < 0 ) {
	    // Ran out of money
	    showGameOverModal();
	    return false;
	}
	if( GD.attackStatus >= 3 ) {
	    // Data exfil
	    showGameOverModal();
	    return false;
	}

	// Made through this level
	GD.level += 1;
	if ( GD.level === GD.levels.length ) {
	    // Show winner modal
	    showWinnerModal();
	} else {
	    // Show success modal
	    showSuccessModal();
	    enterLevel();
	}
    }
    return false;
}

function assessDamage (cost, id) {
    // Budget hits are negative
    GD.budget += cost;
    updateStatus();	

    if( id != 0 ) {
	// eval against deployed mitigations
	var needed = mitreAttack.relationships.filter(o => o.technique === id);
	needed.forEach( function(n) {
	    var m = mitreAttack.mitigations.find(o => o.id === n.mitigation);
	    if( m.inplay === true ) {
		if( m.state != 'on' ) {
		    // Mitigation not in use
		    setMitigationState( m.id, "compromised" );
		}
	    }
	});
    }
}

// Avoiding eval()
function looseParse(obj) { return Function('"use strict";return (' + obj + ')')(); }

function showAlert (action) {
    var m = jQuery('#cardModal');
    var mitrelink = "<div class='d-flex justify-content-center'><br><a target='_blank' href='https://attack.mitre.org/techniques/" 
		    + action.id + "'><h5>Mitre Att&amp;ck: technique details</h5></a></div>";

    
    m.find('.modal-title').text(action.title);
    m.find('.modal-body').html(action.html + "<div>"  + mitrelink + "</div>");

    // Build callback buttons
    var ignBtn = '<button type="button" id="modalBtnIgnore" class="btn btn-default btn-ok" data-dismiss="modal">Ignore</button>';
    if( action.type === 'inject' ) {
	ignBtn = '';
    }
    var btnHtml = [
	'<div class="align-items-center">' + ignBtn,
	'<button type="button" id="modalBtnAccept" ',
	'class="btn btn-default btn-ok bg-danger" data-dismiss="modal">' + action.cost + ' Credits</button></div>',
    ].join("\n");
    m.find('.modal-footer').html(btnHtml);
    if( action.type != 'inject' ) {
	jQuery('#modalBtnIgnore').on('click', function(event) {
	    // TODO add as bypass or remove mitigation from game?
    	    looseParse( "{a:assessDamage(" + action.cost + ",'" + action.id + "')}" );
	    showIncidentModal();
	    event.preventDefault();
        });
    }
    jQuery('#modalBtnAccept').on('click', function(event) {
	looseParse( "{a:assessDamage(" + action.cost + ",'" + action.id + "')}" );
 	showIncidentModal();
	event.preventDefault();
    });
    setTimeout(() => { m.modal('show') }, 500 );
}

$('#cardModal').on('show.bs.modal', function (event) {
});

$('#cardModal').on('hidden.bs.modal', function () {
    showIncidentModal();
});

function showMitigationModal (id) {
    var m = mitreAttack.mitigations.find(o => o.id === id);
    var footer = "<div class='align-items-center'><div><a target='_blank'href='https://attack.mitre.org/mitigations/" + 
		    m.id + "'><h5>Mitre Att&amp;ck: mitigation details</h5></a></div></div>";
    showModal(m.name, m.description, footer );
    return false;
}

function updateStatus () {
    // Update the button to run the game

    // Set color indicator
    let statusColors = ["success","warning", "danger", "dark"];
    let statusText = ['Normal','Breached','Persistance','Data Loss']
    color = statusColors[GD.attackStatus];
    
    // Set stage text
    var html = [
	'<div class="btn-group mb-2" role="group" aria-label="Basic example">',
	'<h4 class="align-self-center text-uppercase fw-bold bg-' + color + ' float-left mr-3">' + statusText[GD.attackStatus] + '<h4>',
	'<h4 class="align-self-center  mr-3">' + GD.levels[GD.level].title + '</h4>',
	'<h4 class="align-self-center mr-3">Credits: ' + GD.budget + '</h4>',
	'</div>',
    ].join("\n");

    var b = document.getElementById("runDefense");
    b.innerHTML = html;
} 

function setMitigationState(id, state) {
    if( GD.budget === 0 ) {
	return;
    }
    
    // Array populated for runDefense()
    var m = mitreAttack.mitigations.find(o => o.id === id);
    m.state = state;
    GD.budget -= 1;
    updateStatus();
    document.getElementById('mitigationCard' + id).style.backgroundColor = colors[state]; 
}		

function flipMitigationState(id) {
    var c;
    var cb = document.getElementById("mitigationCB" + id);
    cb.checked = !cb.checked;
    if(cb.checked) {
	    setMitigationState(id, "on" );
    } else {
	    setMitigationState(id, "off" );
    }
    return true;
}

function createMitigationCard (div, m) {
    // Generate clickable button for each mitigation
    var html = [
	'<div >',
	'<div id="mitigationCard' + m.id + '" class="cardBtn">',
	'<div class="checkbox cardBtnL"><input type="checkbox" id="mitigationCB' + m.id + '" ',
	'value="optionL" onclick="flipMitigationState(\'' + m.id + '\')">',
	'<label for="mitigationCB' + m.id + '"></label></div> ',
	'<button class="cardBtnL" onclick="flipMitigationState(\'' + m.id + '\')">',
	m.name + '</button>',
	'<button class="cardBtnR" onclick="showMitigationModal(\'' + m.id + '\');event.preventDefault();">',
	'<i class="fa fa-info-circle"></i></button></div></div>',
    ].join("\n");
    div.append(html);
    m.inplay = true;
}

    
function enterLevel () {
    // User is entering a new level
    
    // Set phase to pre-compromise
    GD.attackStatus = 0;
    var stage = GD.levels[GD.level];
    GD.budget += stage.levelBudget;
    jQuery("#game").css('background', "url('"+ stage.background + "') no-repeat center center");

    // Add mitigations that become available in this dtage
    mitreAttack.mitigations.forEach(function(element) {
	if( element.level == GD.level + 1 ) {
	    createMitigationCard(jQuery('#mitigationArea'), element );
	}
    });
    
    // Should already be empty at this point
    attackCards = []; // {phase,title,html,type,cost}
    
    // Add bypasses for this level
    for( var i=0; i<GD.levels[GD.level].numberOfBypasses; ++i ) {
	var inplay = GD.bypasses.filter(o => o.used === false);
	var b = inplay[Math.floor(Math.random() * inplay.length)];
	b.used = true;
	var a = {"phase": 0, "title": "Mitigation Failure", "html": b.description, "type": "bypass",
			"id": 0, "cost": -1, "color": colors.red }
	cardQueue.push(a);
    };
    
    // Add injects for this level
    for( var i=0; i<GD.levels[GD.level].numberOfInjects; ++i ) {
	var inplay = GD.injects.filter(o => o.used === false);
	var b= GD.injects[Math.floor(Math.random() * inplay.length)];
	b.used = false;
	var a = {"phase": 0, "title": b.title, "html": b.html, "type": "inject",
			"id": 0, "cost": b.cost, "color": b.color }
	cardQueue.push(a);
    };
    
    // Add attack techniques
    var techniques = [stage.compromises, stage.escalations, stage.exfils ];
    var phase = 0;
    techniques.forEach(function(t) {
	t.forEach(function(id) {
	    var technique = mitreAttack.techniques.find(o => o.technique === id);
	    var a = {"phase": phase, "title": technique.name, "html": technique.description, "type": "technique",
			    "id": technique.technique, "cost": -1 }
	    cardQueue.push(a);
	});
	phase += 1;
    });
    
    // Sort cards into appropriate phases
    cardQueue = cardQueue.sort(function X(a, b) {
	return a.phase > b.phase ?  1 : a.phase < b.phase ? -1 : 0;
    });
    
    // Show the RUN DEFENSE button to user
    updateStatus();	
}


// Read Mitre Att&ck data
mitreAttack = $.ajax({
    url: "MitreAttack.json",
    async: false,
    error: function(xhr, status, error){
	 var errorMessage = xhr.status + ': ' + xhr.statusText
	 alert('Error - MitreAttack.json' + errorMessage);
     }
}).responseJSON;
// Force initial state
mitreAttack.mitigations.forEach(function(m) {
    m.inplay = false;
    m.state = "off";
});


// Read game data
GD = $.ajax({
    url: "game.json",
    async: false,
    error: function(xhr, status, error){
	 var errorMessage = xhr.status + ': ' + xhr.statusText
	 alert('Error - game.json' + errorMessage);
     }
}).responseJSON;
// Force initial state
GD.bypasses.forEach(function(b) { b.used = false; });
GD.injects.forEach(function(m) { m.used = false; });


// Setup the initial gameboard
enterLevel();

var authToken;

// Bypass auth if running from a local server
if (location.hostname === "localhost" || location.hostname === "127.0.0.1") {
    ;
} else {
    Wlowi.authToken.then(function setAuthToken(token) {
	if (token) {
	    authToken = token;
	} else {
	    window.location.href = '/signin.html';
	}
    }).catch(function handleTokenError(error) {
	alert(error);
	window.location.href = '/signin.html';
    });
}

function saveGame() {
    var id = $('#cardModal #gameModalID').val().trim();
   $.ajax({
	method: 'POST',
	url: _config.api.invokeUrl + 'gamesave?id=' +id,
	headers: {
	    Authorization: authToken
	},
	data: JSON.stringify(GD),
	contentType: 'application/json',
	success: function() {
	    $('#cardModal').modal('hide');
	},
	error: function ajaxError(jqXHR, textStatus, errorThrown) {
	    console.error('Error requesting game: ', textStatus, ', Details: ', errorThrown);
	    console.error('Response: ', jqXHR.responseText);
	    alert('An error occured when requesting your game:\n' + jqXHR.responseText);
	}
    });
}

function loadGame() {
    var id = $('#cardModal #gameModalID').val().trim();
    $.ajax({
	method: 'GET',
	url: _config.api.invokeUrl + 'gameload?id=' +id,
	crossOrigin: true,
	headers: {
	    'Authorization': authToken,
	},
	data: '',
	contentType: 'application/json',
	success: function(data) {
	    GD = data.Game;
	    $('#cardModal').modal('hide');
	    enterLevel();
	},
	error: function ajaxError(jqXHR, textStatus, errorThrown) {
	    console.error('Error requesting game: ', textStatus, ', Details: ', errorThrown);
	    console.error('Response: ', jqXHR.responseText);
	    alert('An error occured when requesting your game:\n' + jqXHR.responseText);
	}
    });
}

