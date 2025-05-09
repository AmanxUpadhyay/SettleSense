# SettleSense

<p align="center">
  <img src="settle_sense/static/logo.png" alt="SettleSense Logo" width="200" height="200"/>
</p>

<p align="center">
  <b>Professional Debt Tracking Application</b><br>
  <i>Track debts, credits, and settlements with precision</i>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#screenshots">Screenshots</a> •
  <a href="#development">Development</a> •
  <a href="#license">License</a>
</p>

## Overview

SettleSense is a professional-grade web application designed to track peer-to-peer debts and credits. It provides a clean, intuitive interface for users to log financial transactions, view their net balance, and manage settlements with precision.tleSense Project Plan

## Overview

We’re building a simple web application to track peer-to-peer debts. Users can log what they owe or what’s owed to them and view their net balance at a glance.

## Features

- **💰 Comprehensive Debt Tracking**: Log debts and credits with detailed information
- **📊 Advanced Analytics Dashboard**: Visual representations of your financial situation
- **⏱️ Time-Based Insights**: Track when debts were created and modified
- **🔄 Intuitive Transaction Management**: Add, edit, and delete entries with ease
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🔍 Search & Filter**: Find specific transactions quickly
- **📁 Data Export**: Export your debt records in CSV format
- **🔧 Database Migration System**: Seamlessly upgrade between versions
- **⚙️ Customizable Settings**: Personalize your experience
- **💾 Backup & Restore**: Protect your financial data

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