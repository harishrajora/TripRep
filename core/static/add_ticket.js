document.getElementById('ticket_pdf').addEventListener('change', function(event) {
  console.log("Event triggered");
  if (event.target.files.length > 0) {
    const file = event.target.files[0];
    // File has been selected
    console.log("File selected");
    // document.getElementById('status').textContent = 'Uploading...';
    const formData = new FormData();
    formData.append('file', file);
    // Get CSRF token
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    // Upload the file
    console.log("Reached this point")
    fetch("/create_ticket/", {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            console.log("File uploaded successfully");
            document.querySelector('#ticket_upload_options').style.visibility = 'visible';
        } else {
            document.getElementById('status').textContent = 'Error: ' + data.message;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // document.getElementById('status').textContent = 'Upload failed';
    });
  } else {
    // No file selected
    console.log("No file selected");
    document.querySelector('#ticket_upload_options').style.visibility = 'hidden';
    return;
  }
});