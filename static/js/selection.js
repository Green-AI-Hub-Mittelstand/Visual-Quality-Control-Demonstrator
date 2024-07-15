// This function fetches available video input devices and adds them as options to the dropdown
function loadWebcams() {
    // First, clear existing options
    const dropdown = document.querySelector('.dropdown-menu');
    dropdown.innerHTML = ''; // Clear existing webcam options
  
    navigator.mediaDevices.enumerateDevices()
      .then(devices => {
        devices.forEach(device => {
          if (device.kind === 'videoinput') {
            const option = document.createElement('a');
            option.classList.add('dropdown-item');
            option.href = '#';
            option.text = device.label || `Camera ${device.deviceId.substr(0, 8)}`; // Display device label or fallback text
            option.dataset.deviceId = device.deviceId; // Store deviceId in data attribute for later use
  
            // Append the webcam option to the dropdown
            dropdown.appendChild(option);
          }
        });
      })
      .catch(error => {
        console.error('Error accessing media devices:', error);
      });
  }
  
  // This function sets up an event listener for selecting a webcam from the dropdown
  function setupWebcamSelection() {
    const dropdown = document.querySelector('.dropdown-menu');
    dropdown.addEventListener('click', function(event) {
      event.preventDefault(); // Prevent default anchor behavior
  
      if (event.target.classList.contains('dropdown-item')) {
        // Update the current_webcam variable with the deviceId of the selected webcam
        current_webcam = event.target.dataset.deviceId;
        console.log('Selected webcam:', event.target.text, 'ID:', current_webcam); // For demonstration, showing label and ID
      }
    });
  }
  
  // Call the functions to load webcams and set up the selection handling
  loadWebcams();
  setupWebcamSelection();
  