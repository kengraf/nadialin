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

  // Global variables
  let hunterSid = "";
  let eventStartDate = new Date();
  let eventData = {};
  let countTimer = 0;
 
function sleep(ms) {
   return new Promise(resolve => setTimeout(resolve, ms));
}

async function awaitHunterData() {
  await sleep(500);
}
 
  window.onload = function () {
    // If SID in url. An override only used to ease testing
    const params = new URLSearchParams(window.location.search);
    hunterSid = params.get("sid") || "";

    if( hunterSid === "" ) {
        // Try Auth via the sid value in cookie
        const value = `; ${document.cookie}`;
        const parts = value.split(`; session=`);
        if (parts.length === 2) 
            hunterSid = parts.pop().split(';').shift();
    }

    if( hunterSid === "" ) {
        googleAuthenicate();
        // hunterSid set in callback handleCredentialResponse()
        // Callback re-invokes this page with a cookie on success
        return;
    }
  

    // Get the event data and check start time for event
    fetchEvent();
    fetchScores();
    showScores();
    
    changeContainer(timerContainer);
    countTimer = setInterval( countingDown, 1000 );


}
  
  function googleAuthenicate() {

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
        hunterData = null;
        
        function toggleHunterDialog() {
            let dialog = document.getElementById('hunterContainer');

            fetch('/v1/eventScores')
                .then(response => response.json())
                .then(data => {
                    scoreData = data;
                    hunterData = data['hunter'];
                    picHTML = `<img src="data:image/png;base64, ${hunterData.pictureBytes}" width="80" height="80" style="border-radius:50%;">`;
                    document.getElementById('picture').innerHTML = picHTML

                    document.getElementById('name').innerHTML = hunterData.name;
                    document.getElementById('email').innerHTML = hunterData.email;
                    document.getElementById('squad').innerHTML = hunterData.squad;
                    
                    document.getElementById('needSquad').style.display = "none"
                    document.getElementById('hasSquad').style.display = "none"
                    if( hunterData.squad === "undefined" )  {
                        document.getElementById('needSquad').style.display = "block"
                    }
                    else {
                        document.getElementById('dns').innerHTML = hunterData.squad + ".nadialin.kengraf.com";
                        document.getElementById('hasSquad').style.display = "block"
                    }
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
            if (scoreData["squads"].length === 0) return;
            
            // Create table headers dynamically
//            const headers = Object.keys(scoreData["squads"][0]);
            const headers = ["name", "score", "flag", "login", "red", "blue"]
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
                headers.forEach(col => {
                    let td = document.createElement('td');

                    if ( Array.isArray(row[col])) {
                        td.className = 'button-cell';
                        row[col].forEach(b => {
                            let button = createCopyableButton(b.name, b.color, b.url);
                            td.appendChild(button);
                        });
                    } else if (col == 'login') {
                        if (row[col]) {
                            td.className = 'check'; 
                            td.textContent = '\u2713';
                        } else {
                            td.className = 'cross'; 
                            td.textContent = '\u2715';
                        }
                    } else if (col == 'red' || col == 'blue') {
                        const rb = {"0":'red',"1":'red',"9":'green',"10":'green', };
                        td.style.color = rb[row[col]];
                        td.textContent = row[col];
                    } else if (col == 'flag') {
                        if (row[col] == row['name']) {
                            td.textContent = row[col];
                        } else {
                            let button = createCopyableButton(row[col], 'red', '');
                            td.appendChild(button);
                        }
                    }
                    else {
                        td.textContent = row[col];
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
    function countingDown() {
    
        if( Object.keys(eventData).length === 0) {
            // Wait for fetch to complete
            return true;
        }

        // eventStartDate = new Date("2025-08-21T18:00:00Z");      
        const now = new Date();
        const startTime = new Date(eventData.events[0].startTime);
        const diff = startTime - now;
        
        if (diff <= 0 || eventData.hunters[0].admin ) {
          // Release time has passed, stop counting down
          clearInterval(countTimer);
          showScores();
          return false;
        }
         
      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      daysEl.textContent = days.toString().padStart(2, '0');
      hoursEl.textContent = hours.toString().padStart(2, '0');
      minutesEl.textContent = minutes.toString().padStart(2, '0');
      secondsEl.textContent = seconds.toString().padStart(2, '0');
      return true;
    }
    
