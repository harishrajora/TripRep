# TripRep

An application to save trip information such as tickets and other stuff.

## About this scaffold
This repository contains a small Django starter project with a clean, light homepage.

- Homepage headline: **"Everything about your travels"**
- Login button on the top-right (links to Django admin login)
- Pure CSS styling with subtle transitions (no JS frameworks)
- Automatic superuser creation on `migrate` (username: `hrajora`, password: `hrajora`) — suitable for local development only

## Quick start (Windows PowerShell)

1. Create a virtualenv and activate it:

   python -m venv venv
   .\venv\Scripts\Activate.ps1

2. Install dependencies:

   pip install -r requirements.txt

3. Run migrations (this will create the `hrajora` superuser automatically):

   python manage.py migrate

4. Run the dev server:

   python manage.py runserver

5. Open http://127.0.0.1:8000/ to view the homepage. Use the top-right "Login" button or visit http://127.0.0.1:8000/admin/ to sign in.

**Note:** The automatic superuser creation is convenient for testing and local development. Remove or adapt `core/signals.py` before deploying to production.
