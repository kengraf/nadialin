
var authToken;

// Force signin if needed
Nadialin.authToken.then(function setAuthToken(token) {
    if (token) {
        authToken = token;
        } else {
        window.location.href = '/signin.html';
    }
    }).catch(function handleTokenError(error) {
    alert(error);
    window.location.href = '/signin.html';
    });
        

function save() {
    // TODO: "id" should the user's id
    var id = $('#cardModal #gameModalID').val().trim();
    $.ajax({
       method: 'POST',
        url: _config.api.invokeUrl + 'user/save?id=' +id,
        headers: {
            Authorization: authToken
            },
        data: JSON.stringify(GD),
        contentType: 'application/json',
        success: function() {
            $('#cardModal').modal('hide');
            },
        error: function ajaxError(jqXHR, textStatus, errorThrown) {
            console.error('Error saving user changes: ', textStatus, ', Details: ', errorThrown);
            console.error('Response: ', jqXHR.responseText);
            alert('An error occured when saving youe changes:\n' + jqXHR.responseText);
        }
        });
}

function load() {
    // TODO: "id" should the user's id
    var id = $('#cardModal #gameModalID').val().trim();
    $.ajax({
        method: 'GET',
        url: _config.api.invokeUrl + 'user/load?id=' +id,
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