// Function to extract the task ID from the URL
function getTaskIdFromUrl() {
    const pathArray = window.location.pathname.split('/');
    const analyseIndex = pathArray.indexOf('analyse');
    if (analyseIndex !== -1 && pathArray.length > analyseIndex + 1) {
      return pathArray[analyseIndex + 1];
    }
    return null;
  }
  
  // Function to check the task status
  function checkTaskStatus(taskId) {
    // Using fetch to make a request to the server
    fetch('/analyse/' + taskId)
      .then(response => {
        if (response.ok && response.headers.get('content-type').includes('application/json')) {
          // If the response is JSON, then the task is complete
          return response.json();
        } else {
          // If the response is not JSON, it means the task is still running
          throw new Error('Task still running');
        }
      })
      .then(data => {
        if (data.result === 'SUCCESS') {
          // If the task is successful, redirect to the results page
          window.location.href = '/results/' + taskId;
        }
      })
      .catch(error => {
        console.error('Error:', error);
        // If the task is not yet successful, wait for 1 second and check again
        setTimeout(() => checkTaskStatus(taskId), 1000);
      });
  }
  
  // Extract the task ID from the URL
  const taskId = getTaskIdFromUrl();
  if (taskId) {
    checkTaskStatus(taskId);  // Start checking the task status
  } else {
    console.error('Task ID not found in URL');
  }
  