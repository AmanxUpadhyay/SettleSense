# SettleSense Project Plan

## Overview

We’re building a simple web application to track peer-to-peer debts. Users can log what they owe or what’s owed to them and view their net balance at a glance.

## Tech Stack

* **Backend:** Python Flask
* **Database:** SQLite (lightweight, file-based)
* **Frontend:** HTML/CSS with Bootstrap for styling, vanilla JavaScript for interactivity
* **Templating:** Jinja2 for server-rendered views
* **Development Environment:** virtualenv with `pip`

## MVP Features

1. **Add Debt Entry**

   * Person’s name
   * Amount
   * Direction (you owe them / they owe you)
   * Optional description and date
2. **List & Balance**

   * Display all entries in a table
   * Calculate and show net balance (positive or negative)
3. **Edit & Delete**

   * Modify or remove existing entries
4. **Reminders**

   * Schedule simple email or in-app reminders (optional MVP stretch)
5. **Export**

   * Download statement as CSV (optional MVP stretch)

## Initial Setup Steps

1. **Create a virtual environment and install Flask**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask
   ```
2. **Set up project structure**

   ```
   settle_sense/
   ├── app.py
   ├── requirements.txt
   ├── templates/
   │   └── index.html
   ├── static/
   │   └── style.css
   └── instance/
       └── debts.sqlite
   ```
3. **Initialize `app.py`**

   * Create a basic Flask app with a home route rendering `index.html`
   * Configure SQLite database in `instance/debts.sqlite`

## Next Steps

* Scaffold out `app.py` and the home page template
* Define a `Debt` model and database schema
* Implement CRUD routes for debts