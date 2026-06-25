# [TripRep](https://www.triprep.in)

TripRep is a Django web app for travelers who want one place to store and review trip tickets, reservations, and do much more.  
You can upload ticket and reservation PDFs, organize them into trips, view clean lists and detail pages, record spending in any currency (auto-converted to INR), and track spending statistics. In addition, TripRep comes
with AI agents that can help you book flight tickets, create itineraries, and help answer travel questions (Currently In Progress).

The app also includes an AI-assisted flow that reads a ticket PDF and auto-fills ticket fields using Google Gemini.

## Table of Contents

- [What TripRep Does](#what-triprep-does)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Run the App](#run-the-app)
- [How to Use TripRep](#how-to-use-triprep)
- [Route Guide](#route-guide)
- [Troubleshooting](#troubleshooting)
- [Production and Security Notes](#production-and-security-notes)
- [Contributing](#contributing)

## What TripRep Does

TripRep currently focuses on travel management:

- User signup, login, logout, profile updates, and password changes
- Per-user preferred currency, with amounts auto-converted to INR using daily exchange rates
- Ticket creation with manual entry fields, filled automatically with the help of AI after upload
- Reservation creation with manual entry fields
- Ticket/reservation PDF upload and thumbnail generation (first page preview)
- AI extraction endpoint to read uploaded PDF tickets and prefill fields
- Ticket list view and individual ticket detail pages with a quick-to-see image of the ticket
- Reservation list view and individual reservation detail pages
- Trip creation, plus linking tickets and reservations to a trip — from the add pages, a standalone attach page, or while creating the trip
- Trip detail page that lists attached tickets and reservations with a Tickets/Reservations/All filter
- Statistics page to get a glance at spending across platforms, flights, hotels, and more, plus a TripRep score
- AI agents to book tickets and create itineraries (in progress)


## Tech Stack

- Python 3
- Django 4.2+
- SQLite (default local database)
- `google-genai` for Gemini ticket parsing
- PyMuPDF (`fitz`) + Pillow for ticket thumbnail generation
- `python-dotenv` for loading environment variables
- Cached exchange rates (`static/core/exchange_rates.json`) for multi-currency to INR conversion

## Project Structure

```text
TripRep/
├── manage.py
├── requirements.txt
├── README.md
├── TripRep/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── core/
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    ├── signals.py
    ├── templates/core/
    └── static/
```

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd TripRep
```

### 2. Create and activate a virtual environment

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
genai_api_key=YOUR_GOOGLE_GENAI_API_KEY
```

Important: the key name is `genai_api_key` (lowercase), matching `TripRep/settings.py`.

### 5. Run migrations

```bash
python manage.py migrate
```

During migration, a default superuser is auto-created by `core/signals.py`:

- Username: `hrajora`
- Password: `hrajora`

This is for local development only. Change or remove this behavior before any production use.

## Environment Variables

TripRep currently reads:

- `genai_api_key`: API key used by the Gemini integration in ticket extraction.

If this is missing, AI ticket processing (`/create_ticket/`) will fail.

## Run the App

Start the development server:

```bash
python manage.py runserver
```

Open:

- App home: `http://127.0.0.1:8000/`
- Login: `http://127.0.0.1:8000/login/`
- Admin: `http://127.0.0.1:8000/admin/`

## How to Use TripRep

### Flow 1: Create an account and access dashboard

1. Visit `/signup/`
2. Register with email and password
3. After signup/login, go to `/dashboard/`

### Flow 2: Add a ticket

1. Go to `/add_ticket/`
2. Upload a ticket PDF.
3. Let the automatic parser fill all details automatically.
4. Review and edit the title, source, destination, type, booked-through, date, and amount if required.
5. Optionally attach the ticket to an existing trip using the trip dropdown.
6. Submit to save ticket.

### Flow 3: Add a reservation

1. Go to `/add_reservation/`
2. Upload a reservation PDF.
3. Review and edit the fields.
4. Optionally attach the reservation to an existing trip using the trip dropdown.
5. Submit to save the reservation.

### Flow 4: Use AI ticket extraction

1. On `/add_ticket/`, select a PDF
2. Frontend JS posts the file to `/create_ticket/`
3. Backend calls Gemini, parses the response, and returns extracted fields
4. Form fields auto-populate in the browser
5. Submit to persist the ticket

### Flow 5: Review saved tickets

1. Open `/tickets/` for your personal ticket list
2. Click a ticket to open `/view_ticket/<ticket_id>/`
3. View metadata, thumbnail, and downloadable file
4. Delete a ticket from the ticket detail page if needed

### Flow 6: Create and review trips

1. Go to `/add_trip/` and fill in the trip name, description, type, and start/end dates
2. Optionally pick one unattached ticket and one unattached reservation to link
3. Save the trip, then open it at `/view_trip/<trip_id>/`
4. On the trip page, use the Tickets/Reservations/All filter to review attached items
5. You can also attach an existing ticket to a trip later from `/attach_trip/<ticket_id>/`

### Flow 7: View summary stats

Open `/statistics/` to see a spending dashboard with charts, including:

- Total ticket count
- Total spending amount (in INR)
- Counts and spending grouped by ticket type and booking platform

## Route Guide

Routes from `core/urls.py`:

Accounts and pages

- `/` home page
- `/about_triprep/` about page
- `/signup/` user registration
- `/login/` user login
- `/logout/` user logout
- `/dashboard/` post-login dashboard
- `/profile/` profile page
- `/update_profile/` profile update action (POST)
- `/updatepassword/` change password
- `/ai-world/` AI features landing (in progress)

Tickets

- `/tickets/` ticket listing
- `/add_ticket/` add ticket form
- `/create_ticket/` AI extraction endpoint (POST)
- `/process_ticket_pdf/` PDF processing endpoint
- `/save_ticket/` save ticket endpoint (POST)
- `/view_ticket/<ticket_id>/` ticket details
- `/delete_ticket/<ticket_id>/` delete ticket

Reservations

- `/reservations/` reservation listing
- `/add_reservation/` add reservation form
- `/save_reservation/` save reservation endpoint (POST)
- `/view_reservation/<reservation_id>/` reservation details
- `/delete_reservation/<reservation_id>/` delete reservation

Trips

- `/trips/` trip listing
- `/add_trip/` create a trip and optionally link a ticket/reservation
- `/view_trip/<trip_id>/` trip details with Tickets/Reservations/All filter
- `/attach_trip/<ticketID>/` attach an existing ticket to a trip

Statistics and misc

- `/statistics/` spending statistics dashboard
- `/statistics/data/` statistics data endpoint (JSON, used by charts)
- `/booking_saved/` booking confirmation page
- `/robots.txt` robots file

## Troubleshooting

### AI extraction fails

- Verify `.env` exists in project root.
- Confirm `genai_api_key` is valid.
- Ensure uploaded file is a readable PDF.

### Ticket thumbnail not generated

- Check that PyMuPDF and Pillow installed correctly.
- Confirm uploaded file is not corrupted.
- Ensure media files are writable in your environment.

### Static or media files not showing in development

- Keep `DEBUG = True` for local development.
- Confirm URLs are loaded through Django (`/static/...`, `/media/...`).

### Login issues

- Ensure migrations completed successfully.
- Use the default local superuser only for local testing or create a new user in admin.

## Production and Security Notes

Before deployment, update the following:

- Remove or secure auto-created default superuser in `core/signals.py`.
- Set a real `SECRET_KEY` and move it to environment variables.
- Set `DEBUG = False`.
- Set a proper `ALLOWED_HOSTS` list.
- Configure production static/media serving.
- Review AI response parsing and add validation/error handling.
- Add logging instead of `print` statements.

## Contributing

Contributions are welcome. A practical workflow:

1. Create a feature branch
2. Make focused changes
3. Run migrations/tests as needed
4. Open a pull request with a clear description of behavior changes
