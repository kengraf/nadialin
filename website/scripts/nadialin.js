// Mobile menu toggle
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');

hamburger.addEventListener('click', () => {
  mobileMenu.classList.toggle('active');
});

// Only one contianer is active(visible) at a time
const loginContainer = document.getElementById('loginContainer');
const hunterContainer = document.getElementById('hunterContainer');
const eventContainer = document.getElementById('eventContainer');
const faqContainer = document.getElementById('faqContainer');
const docsContainer = document.getElementById('docsContainer');
const scoreContainer = document.getElementById('scoreContainer');
let currentContainer = docsContainer;

// Untargeted/canvas click shows score container
function showScores() {
  changeContainer(scoreContainer);
}

// No "login button"; js forces loginContainer if no uuid provided in URL
document.getElementById("hunterButton").addEventListener("click", function() {
  changeContainer(hunterContainer);
  toggleHunterDialog();
});
document.getElementById("eventButton").addEventListener("click", function() {
  changeContainer(eventContainer);
});
document.getElementById("faqButton").addEventListener("click", function() {
  changeContainer(faqContainer);
});
document.getElementById("docButton").addEventListener("click", function() {
  changeContainer(docsContainer);
});
document.getElementById("scoreButton").addEventListener("click", function() {
  changeContainer(scoreContainer);
});

function changeContainer(newActive) {
        if (currentContainer) {
          currentContainer.style.display = 'none';
        }
        currentContainer = newActive;
        currentContainer.style.display = 'flex';
}

function handleCredentialResponse(response) {
    const idToken = response.credential;

    // Send the token to your backend via POST
    fetch('/v1/verifyToken', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ idToken }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Token verification failed: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Data fetched:', data);
        window.location.href = '/index.html';
      })
      .catch(error => {
        console.error('Error verifying token:', error);
      });
  }

  window.onload = function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    showScores()
    if ( fetchScores() )
      // Active user; no need to login   
      return;
    if ( window.location.hostname === "localhost" )
      // If localhost we are just testing
      return;

    loginContainer.style.display = 'flex';
    currentContainer = googleAuthenicate();
    showScores()
}
  
  function googleAuthenicate() {
    // Render the Google Sign-In button
    google.accounts.id.initialize({
      client_id: '1030435771551-qnikf54b4jhlbdmm4bkhst0io28u11s4.apps.googleusercontent.com',
      callback: handleCredentialResponse,
    });
    
    // Auto-popup dailog (top left) or Button to start browser popup to confirm
    // Pick 1
    
    // Browser popup confirmation style
    google.accounts.id.renderButton(
      document.getElementById('googleOIDCbutton'),
      { theme: 'filled_blue', size: 'large', shape: "pill" }
    );
    
    // Auto popup dialog style
    // google.accounts.id.prompt();
  };
  
// -------------- hunter profile code ----------------- //
        let hunterData = null;
        
        function toggleHunterDialog() {
            let dialog = document.getElementById('hunterContainer');

            fetch('/v1/eventScores')
                .then(response => response.json())
                .then(data => {
                    hunterData = data['hunter'];
                    picHTML = `<img src="${data.picture}" width="80" height="80" style="border-radius:50%;">`;
                    document.getElementById('picture').innerHTML = picHTML

                    document.getElementById('name').textContent = data.name;
                    document.getElementById('email').textContent = data.email;
                    document.getElementById('ip').textContent = data.ip;
                    document.getElementById('dns').textContent = data.dns;
                    
                    let squadDropdown = document.getElementById('squad');
                    squadDropdown.innerHTML = '';
                    data.squadList.forEach(member => {
                        let option = document.createElement('option');
                        option.value = member.name;
                        option.textContent = member.name;
                        squadDropdown.appendChild(option);
                    });
                    squadDropdown.value = data.squad;
                    updateSquadList(null);
                    
                    dialog.style.display = 'flex';
                })
                .catch(error => console.error('Error fetching data:', error));
        }

        function updateSquadList(event) {
            if( event ) { event.stopPropagation(); }
            if (!hunterData) return;
            let selectedSquad = document.getElementById('squad').value;
            let squadListElement = document.getElementById('squadList');
            squadListElement.innerHTML = '';
            
            hunterData.squadList.filter(member => member.flag === selectedSquad).forEach(member => {
                let li = document.createElement('li');
                li.innerHTML = `<img src="${member.picture}" width="30" height="30" style="border-radius:50%;"> ${member.name} (${member.flag})`;
                squadListElement.appendChild(li);
            });
        }

        function copyToClipboard(event, elementId, iconElement) {
            event.stopPropagation()
            const text = document.getElementById(elementId).textContent;
            navigator.clipboard.writeText(text).then(() => {
                iconElement.classList.add('copied');
                setTimeout(() => {
                    iconElement.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Error copying text: ', err);
            });
        }
        
        function updateHunter(event) {
            alert('TODO: Enable hunter updating!');
        }

// ------------------ Event information code ---------------------- //
    const jsonData = {
    "events": [
        { "name": "nadialin" }
    ],
    "hunters": [
        { "name": "wooba" },
        { "name": "wooba2" }
    ],
    "squads": [
        { "name": "goobas" },
        { "name": "bear" }
    ],
    "machines": [
        { "name": "nadialin" }
    ],
    "instances": [],
    "services": []
    };

    function filter(menuLabel, subLabel = null) {
    if (subLabel) {
        console.log(`Filtering by: ${menuLabel} > ${subLabel}`);
    } else {
        console.log(`Filtering by: ${menuLabel}`);
    }
    }

    function createMenuFromData(data) {
    const menu = document.getElementById('menu');
    menu.innerHTML = '';

    Object.keys(data).forEach((key) => {
        const items = data[key];
        if (items.length === 0) return; // Skip empty sections

        const wrapper = document.createElement('div');
        wrapper.className = 'has-editSubmenu';

        const parentLink = document.createElement('a');
        parentLink.textContent = `${key} ▸`;
        parentLink.onclick = (event) => {
        event.stopPropagation();
        filter(key);
        };

        const editSubmenu = document.createElement('div');
        editSubmenu.className = 'editSubmenu';

        items.forEach(item => {
        if (item.name) {
            const subLink = document.createElement('a');
            subLink.textContent = item.name;
            subLink.onclick = (event) => {
            event.stopPropagation();
            filter(key, item.name);
            };
            editSubmenu.appendChild(subLink);
        }
        });

        wrapper.appendChild(parentLink);
        wrapper.appendChild(editSubmenu);
        menu.appendChild(wrapper);
    });
    }

    // Simulate fetch
    window.onload = () => {
    // If fetching from an endpoint, use:
    // fetch('your-endpoint.json')
    //   .then(response => response.json())
    //   .then(data => createMenuFromData(data));

    createMenuFromData(jsonData); // For this example, use static jsonData
    };
        
// ----------------------- Scoring code --------------------------- //
        let sortDirections = {};
        let scoreData = {}
        
        function fetchScores() {
            fetch('/v1/eventScores')
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                console.log("Data:", data);
                populateTable(data);
                return true;
              })
              .catch(err => {
                console.error("Fetch failed:", err);
                return false;
              });
        }
        
        function populateTable(scoreData) {
            const tableHeader = document.getElementById('table-header');
            const tableBody = document.getElementById('table-body');
            
            if (scoreData.length === 0) return;
            
            // Create table headers dynamically
            const headers = Object.keys(scoreData["squads"][0]);
            headers.forEach(header => {
                let th = document.createElement('th');
                if (header === 'Services') {
                    th.innerHTML = "Service Status";
                } else {
                    th.innerHTML = `${header} <span class='sort-icon'>▲▼</span>`;
                }
                th.onclick = () => sortTable(header, th);
                tableHeader.appendChild(th);
                sortDirections[header] = 'asc';
            });
            
            tableBody.innerHTML = '';
            scoreData["squads"].forEach(row => {
                let tr = document.createElement('tr');
                headers.forEach(header => {
                    let td = document.createElement('td');

                    if ( Array.isArray(row[header])) {
                        td.className = 'button-cell';
                        row[header].forEach(b => {
                            let button = createCopyableButton(b.name, b.color, b.url);
                            td.appendChild(button);
                        });
                    } else {
                        td.textContent = row[header];
                    }
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });
        }
        
        function createCopyableButton(text, color, url) {
            let button = document.createElement('button');
            button.className = 'flag-box';
            button.textContent = text;
            button.style.backgroundColor = color;
            button.style.borderColor = color;
            button.onclick = () => {
                navigator.clipboard.writeText(url).then(() => {
                    alert(`Copied to the clipboard the following service command:\n\n ${url}`);
                });
            };
            return button;
        }

        
        function sortTable(column, thElement) {
            const tableBody = document.getElementById('table-body');
            const rows = Array.from(tableBody.querySelectorAll('tr'));
            const columnIndex = Array.from(document.getElementById('table-header').children).findIndex(th => th.textContent.includes(column));
            const direction = sortDirections[column] === 'asc' ? 1 : -1;

            const sortedRows = rows.sort((a, b) => {
                const aText = a.children[columnIndex].textContent.trim();
                const bText = b.children[columnIndex].textContent.trim();
                
                return isNaN(aText) || isNaN(bText) ? direction * aText.localeCompare(bText) : direction * (aText - bText);
            });
            
            tableBody.innerHTML = '';
            sortedRows.forEach(row => tableBody.appendChild(row));
            
            // Toggle sort direction
            sortDirections[column] = sortDirections[column] === 'asc' ? 'desc' : 'asc';
            thElement.querySelector('.sort-icon').textContent = sortDirections[column] === 'asc' ? '▲▼' : '▼▲';
        }

