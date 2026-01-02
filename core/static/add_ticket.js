document.getElementById('ticket_pdf').addEventListener('change', function(event) {
  console.log("Event triggered");
  if (event.target.files.length > 0) {
    // File has been selected
    console.log("File selected");
    document.querySelector('#ticket_upload_options').style.visibility = 'visible';
  }
});