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
const squadContainer = document.getElementById('squadContainer');
const timerContainer = document.getElementById('timerContainer');
const docsContainer = document.getElementById('docsContainer');
const scoreContainer = document.getElementById('scoreContainer');
let currentContainer = docsContainer;

// Untargeted/canvas click shows score container
function showScores() {
  changeContainer(scoreContainer);
}

const editable = document.querySelector('[contenteditable]');
editable.addEventListener('click', (event) => {
  event.stopPropagation();
  console.log('Clicked editable element');
});

// No "login button"; js forces loginContainer if no uuid provided in URL
document.getElementById("hunterButton").addEventListener("click", function() {
  changeContainer(hunterContainer);
  toggleHunterDialog();
});
document.getElementById("eventButton").addEventListener("click", function() {
    // If fetching from an endpoint, use:
    // fetch('your-endpoint.json')
    //   .then(response => response.json())
    //   .then(data => createMenuFromData(data));
    
    fetchEvent();
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
        data = response.json();
      })
      .then(data => {
        console.log('Data fetched:', data);
        window.location.href = '/index.html';
      })
      .catch(error => {
        console.error('Error verifying token:', error);
      });
  }

  let hunterSid = "";
  let eventStartDate = new Date();
  let eventData = {};
  window.onload = function () {
    // Find SID in url. used to ease testing
    const params = new URLSearchParams(window.location.search);
    var hunterSid = params.get("sid") || "";

    if( hunterSid === "" ) {
        // Try session cookie
        const value = `; ${document.cookie}`;
        const parts = value.split(`; session=`);
        if (parts.length === 2) 
            hunterSid = parts.pop().split(';').shift();
    }

    if( hunterSid === "" ) {
        googleAuthenicate();
        // hunterSid set in callback handleCredentialResponse()
    }
    else {
      setTimeout(() => {
        // Loop until auth completed
        initialPaint();
      }, 1000);
    }
}

function initalPaint() {
    if( hunterSid === "" ) return; // Auth not complete
  
    fetchScores();
    showScores();
      // Initialize countdown
    fetchEvent();
    console.log("Global data (after async):", eventData);
    updateCountdown();
    setInterval(updateCountdown, 1000);
    changeContainer(squadContainer);
}
  
  function googleAuthenicate() {
    if ( window.location.hostname === "localhost" )
        // No auth, just fall back to public mode
        return;
        
    // Render the Google Sign-In button
    changeContainer(loginContainer);

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
  
        function fetchEvent() {
            fetch('/v1/backupEvent')
              .then(response => {
                if (!response.ok) {
                  throw new Error(`HTTP error ${response.status}`);
                }
                return response.json();
              })
              .then(data => {
                console.log("Data:", data);
                eventData = data;
                eventStartDate = new Date(data.events[0].startTime);
                createMenuFromEventData(data);
                return true;
              })
              .catch(err => {
                console.error("Fetch failed:", err);
                return false;
              });
        }
        

    function filter(menuLabel, subLabel = null) {
        let item = {}
        if (subLabel) {
            console.log(`Filtering by: ${menuLabel} > ${subLabel}`);
            for (let d of eventData[menuLabel]) {
                if( d['name'] === subLabel )
                    item = d;
            }
        } else {
            console.log(`Filtering by: ${menuLabel}`);
            item = eventData[menuLabel];
        }
        console.log( item );
        const formatted = JSON.stringify(item, null, 2);
        document.getElementById("editItems").innerHTML = `<pre>${formatted}</pre>`;

    }

    function createMenuFromEventData() {
        const menu = document.getElementById('menu');
        menu.innerHTML = '';
    
        const menuBar = document.getElementById('menuBar');

        // Loop over each primary key
        for (const key in eventData) {
            const menuItem = document.getElementById(key+'-menuItem');;
            menuItem.className = 'menu-item';
            const value = eventData[key];
            const dropdown = document.createElement('div');
            dropdown.className = 'dropdown-content';
         
            if (Array.isArray(value) && value.length > 0) {
               // Sort items by name alphabetically
                const sortedItems = value
                    .filter(item => item.name) // only items that have a name
                    .sort((a, b) => a.name.localeCompare(b.name));
            
                sortedItems.forEach(item => {
                    const subLink = document.createElement('a');
                    subLink.href = '#';
                    subLink.textContent = item.name;
                    subLink.onclick = (event) => {
                        event.stopPropagation();
                        filter(key, item.name);
                        };
                    dropdown.appendChild(subLink);
                });
            
                menuItem.style.display = "block";
                menuItem.appendChild(dropdown);

            }
            menuBar.appendChild(menuItem);
        }


    }

        
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
                scoreData = data;
                populateScores();
                return true;
              })
              .catch(err => {
                console.error("Fetch failed:", err);
                return false;
              });
        }
        
        function populateScores() {
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

// --------------------- time functions ------------------- //
    // The start date is set in the eventData by the event admin
    
    // Elements
    const daysEl = document.getElementById('days');
    const hoursEl = document.getElementById('hours');
    const minutesEl = document.getElementById('minutes');
    const secondsEl = document.getElementById('seconds');

    
    // Update countdown timer
    function updateCountdown() {

    // eventStartDate = new Date("2025-08-17T17:32:28Z");
    if(Object.keys(eventData).length === 0) return;
    console.log("eventStartDate:", eventData.events[0].startTime);
  
    const now = new Date();
    const startTime = new Date(eventData.events[0].startTime);
    const diff = startTime - now;
    
    if (diff <= 0) {
      // Release time has passed
      daysEl.textContent = "00";
      hoursEl.textContent = "00";
      minutesEl.textContent = "00";
      secondsEl.textContent = "00";
      return;
    }
     
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      daysEl.textContent = days.toString().padStart(2, '0');
      hoursEl.textContent = hours.toString().padStart(2, '0');
      minutesEl.textContent = minutes.toString().padStart(2, '0');
      secondsEl.textContent = seconds.toString().padStart(2, '0');
      
    }
    
