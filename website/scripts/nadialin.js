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

    // Dailogs openby buttons
    const openDialogButton = document.getElementById('openHacker');
    const closeDialogButton = document.getElementById('closeHacker');
    const dialogContainer = document.getElementById('hackerContainer');

    openDialogButton.addEventListener('click', () => {
      dialogContainer.style.display = 'flex';
    });

    // Close dialog
    closeDialogButton.addEventListener('click', () => {
      dialogContainer.style.display = 'none';
    });

    // Close dialog when clicking on the overlay
    dialogContainer.addEventListener('click', (event) => {
      if (event.target === dialogContainer) {
        dialogContainer.style.display = 'none';
      }
    });

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

  // Render the Google Sign-In button
  window.onload = function () {
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
