(function () {
  const fileInput = document.getElementById("ticket_pdf");
  const ticketUploadOptions = document.getElementById("ticket_upload_options");
  const saveTicketButton = document.getElementById("save_ticket_btn");
  const ticketProcessingLoader = document.getElementById("ticket_processing_loader");
  const ticketUploadError = document.getElementById("ticket_upload_error");

  if (
    !fileInput ||
    !ticketUploadOptions ||
    !saveTicketButton ||
    !ticketProcessingLoader ||
    !ticketUploadError
  ) {
    return;
  }

  const datePattern = /^\d{4}-\d{2}-\d{2}$/;

  function setLoading(isLoading) {
    ticketProcessingLoader.hidden = !isLoading;
    fileInput.disabled = isLoading;
  }

  function setFormVisible(isVisible) {
    ticketUploadOptions.hidden = !isVisible;
    saveTicketButton.hidden = !isVisible;
  }

  function setError(message) {
    if (!message) {
      ticketUploadError.hidden = true;
      ticketUploadError.textContent = "";
      return;
    }
    ticketUploadError.hidden = false;
    ticketUploadError.textContent = message;
  }

  function setInputValue(id, value) {
    const inputElement = document.getElementById(id);
    if (!inputElement) {
      return;
    }
    inputElement.value = value || "";
  }

  function setDateValue(id, value) {
    const inputElement = document.getElementById(id);
    if (!inputElement) {
      return;
    }
    const dateValue = typeof value === "string" ? value.trim() : "";
    inputElement.value = datePattern.test(dateValue) ? dateValue : "";
  }

  async function uploadAndProcessTicket(file) {
    const formData = new FormData();
    formData.append("file", file);

    const csrfTokenInput = document.querySelector("[name=csrfmiddlewaretoken]");
    if (!csrfTokenInput) {
      throw new Error("Missing CSRF token");
    }

    const response = await fetch("/create_ticket/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfTokenInput.value,
      },
      body: formData,
    });

    let responseData;
    try {
      responseData = await response.json();
    } catch (error) {
      throw new Error("Invalid JSON response");
    }

    if (response.ok && responseData.status === "success") {
      return { ok: true, data: responseData };
    }

    return { ok: false, data: responseData };
  }

  fileInput.addEventListener("change", async function (event) {
    const file = event.target.files && event.target.files[0];
    if (!file) {
      setLoading(false);
      setFormVisible(false);
      setError(null);
      return;
    }

    setFormVisible(false);
    setLoading(true);
    setError(null);

    try {
      const result = await uploadAndProcessTicket(file);
      if (result.ok) {
        const ticketData = result.data.ticket_data || {};
        setInputValue("title", ticketData["Title"]);
        setInputValue("source", ticketData["Source"]);
        setInputValue("destination", ticketData["Destination"]);
        setInputValue("description", ticketData["Description"]);
        setDateValue("date_of_journey", ticketData["Date of Journey"]);
        setInputValue("booked_through", ticketData["Booked Through"]);
        setFormVisible(true);
        return;
      }

      setError(
        result.data && result.data.message
          ? result.data.message
          : "Ticket extraction failed. Please fill in the details manually."
      );
      setFormVisible(true);
    } catch (error) {
      console.error("Error while uploading ticket:", error);
      setError("Unable to process the ticket right now. Please fill in the details manually.");
      setFormVisible(true);
    } finally {
      setLoading(false);
      fileInput.disabled = false;
    }
  });

  setLoading(false);
  setFormVisible(false);
  setError(null);
})();
