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
            // console.log(response);
            console.log("Data::::");
            console.log(data);
            title = data.ticket_data['Title'];
            source = data.ticket_data['Source'];
            destination = data.ticket_data['Destination'];
            // ticket_type = data.ticket_data['Ticket Type'];
            description = data.ticket_data['Description'];
            date_of_journey = data.ticket_data['Date of Journey'];
            booked_through = data.ticket_data['Booked Through'];
            amount_paid = data.ticket_data['Amount'];
            document.querySelector('#title').value = title;
            document.querySelector('#source').value = source;
            document.querySelector('#destination').value = destination;
            // document.querySelector('#ticket_type').value = ticket_type;
            document.querySelector('#description').value = description;
            document.querySelector('#date_of_journey').value = date_of_journey;
            document.querySelector('#booked_through').value = booked_through;
            document.querySelector('#amount_paid').value = amount_paid;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        // document.getElementById('status').textContent = 'Upload failed';
    });
    document.querySelector('#ticket_upload_options').style.visibility = 'visible';
  } else {
    // No file selected
    console.log("No file selected");
    document.querySelector('#ticket_upload_options').style.visibility = 'hidden';
    return;
  }
});