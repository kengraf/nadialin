// TODO: do we care if not valid?
function checkSessionCookie() {
  const cookies = document.cookie;
  const sessionCookie = cookies.split('; ').find(row => row.startsWith('session='));

  if (!sessionCookie) {
    window.location.href = "/login.html"; 
  }
}

    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const mobileMenu = document.getElementById('mobileMenu');

    hamburger.addEventListener('click', () => {
      mobileMenu.classList.toggle('active');
    });

    // Only one contianer is active(visible) at a time
    const loginContainer = document.getElementById('loginContainer');
    const hackerContainer = document.getElementById('hackerContainer');
    const eventContainer = document.getElementById('eventContainer');
    const faqContainer = document.getElementById('faqContainer');
    const docsContainer = document.getElementById('docsContainer');
    const scoreContainer = document.getElementById('scoreContainer');
    let currentContainer = docsContainer;

    // Untarget click shows score container
    function showScores() {
      changeContainer(scoreContainer);
    }
    
    // No "login button"; js forces loginContainer if no uuid provided in URL
    document.getElementById("hackerButton").addEventListener("click", function() {
      changeContainer(hackerContainer);
      toggleHackerDialog();
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
        const sub = `uuid=${data["uuid"]}&idToken=${data["idToken"]}`;
        window.location.href = `/dashboard.html?${sub}`;
      })
      .catch(error => {
        console.error('Error verifying token:', error);
      });
  }

  window.onload = function () {
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    if (urlParams.get('uuid')) {
      // Active user; no need to login   
      return;
    } else {
       loginContainer.style.display = 'flex';
       currentContainer = googleAuthenicate();
    }
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
  
// -------------- hacker profile code ----------------- //
        let hackerData = null;
        
        function toggleHackerDialog() {
            let dialog = document.getElementById('hackerContainer');

            fetch('data3.json') // Replace with actual API endpoint if needed
                .then(response => response.json())
                .then(data => {
                    hackerData = data;
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
            if (!hackerData) return;
            let selectedSquad = document.getElementById('squad').value;
            let squadListElement = document.getElementById('squadList');
            squadListElement.innerHTML = '';
            
            hackerData.squadList.filter(member => member.flag === selectedSquad).forEach(member => {
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
        
        function updateHacker(event) {
            alert('TODO: Enable hacker updating!');
        }

// ------------------ Event information code ---------------------- //
// ----------------------- Scoring code --------------------------- //
        let sortDirections = {};
        let scoreData = {}
        
        async function fetchScores() {
            const response = await fetch('/eventScores');
            scoreData = await response.json();
            populateTable();
        }
        
        function populateTable() {
            const tableHeader = document.getElementById('table-header');
            const tableBody = document.getElementById('table-body');
            
            if (scoreData.length === 0) return;
            
            // Create table headers dynamically
            const headers = Object.keys(scoreData[0]);
            headers.forEach(header => {
                let th = document.createElement('th');
                if (header === 'Service status') {
                    th.innerHTML = `${header}`;
                } else {
                    th.innerHTML = `${header} <span class='sort-icon'>▲▼</span>`;
                }
                th.onclick = () => sortTable(header, th);
                tableHeader.appendChild(th);
                sortDirections[header] = 'asc';
            });
            
            tableBody.innerHTML = '';
            scoreData.forEach(row => {
                let tr = document.createElement('tr');
                headers.forEach(header => {
                    let td = document.createElement('td');
                    if (header === 'Flag' && typeof row[header] === 'object') {
                        td.className = 'flag-cell';
                        let button = createCopyableButton(row[header].name, row[header].color, row[header].url);
                        td.appendChild(button);
                    } else if (header === 'Service status' && Array.isArray(row[header])) {
                        td.className = 'service-cell';
                        row[header].forEach(service => {
                            let button = createCopyableButton(service.name, service.color, service.url);
                            td.appendChild(button);
                        });
                    } else {
                        td.textContent = row[header] || '';
                    }
                    tr.appendChild(td);
                });
                tableBody.appendChild(tr);
            });
        }
        
        function createCopyableButton(text, color, url) {
            let button = document.createElement('button');
            button.className = 'flag-text';
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
        
        fetchScores();
