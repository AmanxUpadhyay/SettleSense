#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SettleSense - A professional debt tracking application.

This application helps users track personal debts and credits
between themselves and others in a clean, organized interface.
"""

import os
import sqlite3
import datetime
from flask import Flask, g, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Application Constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'instance', 'debts.sqlite')

# Flask Application Configuration
app = Flask(__name__)
app.config.update(
    DATABASE=DATABASE,
    DEBUG=os.environ.get('DEBUG', 'False').lower() == 'true',
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
)

# Ensure instance folder exists
os.makedirs(os.path.dirname(app.config['DATABASE']), exist_ok=True)

# Database Connection Management
def get_db():
    """Create and return a database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exc):
    """Close the database connection at the end of a request."""
    db = getattr(g, '_database', None)
    if db:
        db.close()

def init_db():
    """Initialize the database schema if it doesn't exist."""
    db = get_db()
    
    try:
        # First check if the table exists and what columns it has
        cursor = db.execute("PRAGMA table_info(debt)")
        columns = {row['name'] for row in cursor.fetchall()}
        
        if not columns:
            app.logger.info("Creating new debt table with complete schema")
            # Table doesn't exist, create it with all columns
            db.execute('''
                CREATE TABLE debt (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person TEXT NOT NULL,
                    amount REAL NOT NULL,
                    direction TEXT CHECK(direction IN ('you_owe','they_owe')) NOT NULL,
                    note TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
        else:
            app.logger.info(f"Existing table found with columns: {', '.join(columns)}")
            # Table exists, check if it needs to be updated
            if 'created_at' not in columns:
                app.logger.info("Adding created_at column")
                db.execute('ALTER TABLE debt ADD COLUMN created_at TEXT')
            if 'updated_at' not in columns:
                app.logger.info("Adding updated_at column")
                db.execute('ALTER TABLE debt ADD COLUMN updated_at TEXT')
                
        db.commit()
        app.logger.info("Database schema initialization completed successfully")
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Database initialization error: {str(e)}")
        db.rollback()
        return False
    
# Helper function to update any null timestamps in existing data
def update_null_timestamps():
    """Update any null timestamps in the database with the current time."""
    db = get_db()
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # First check if the timestamps columns exist
        cursor = db.execute("PRAGMA table_info(debt)")
        columns = {row['name'] for row in cursor.fetchall()}
        
        updated_rows = 0
        
        if 'created_at' in columns:
            result = db.execute('UPDATE debt SET created_at = ? WHERE created_at IS NULL', (now,))
            updated_rows += result.rowcount
            
        if 'updated_at' in columns:
            result = db.execute('UPDATE debt SET updated_at = ? WHERE updated_at IS NULL', (now,))
            updated_rows += result.rowcount
        
        db.commit()
        app.logger.info(f"Updated timestamps for {updated_rows} rows")
        return True
    except sqlite3.Error as e:
        app.logger.error(f"Error updating timestamps: {str(e)}")
        db.rollback()
        return False

# Database migration route
@app.route('/migration')
def migration():
    """Show database migration page."""
    current_year = datetime.datetime.now().year
    error = request.args.get('error')
    message = request.args.get('message')
    error_details = request.args.get('details')
    
    return render_template(
        'migration.html', 
        current_year=current_year,
        error=error,
        message=message,
        error_details=error_details
    )

# Run initialization when the application starts
database_ready = False
with app.app_context():
    try:
        database_ready = init_db()
        if database_ready:
            update_null_timestamps()
    except Exception as e:
        app.logger.error(f"Failed to initialize database: {str(e)}")
        database_ready = False

# Data Formatting Helpers
def format_currency(value):
    """Format a numeric value as currency."""
    return f"${abs(value):.2f}"

def format_date(value):
    """Format a date string nicely."""
    if not value:
        return "N/A"
        
    try:
        # Try different date formats
        if 'T' in value:
            # ISO format with T separator
            dt = datetime.datetime.fromisoformat(value)
        elif ' ' in value:
            # SQLite format with space separator
            dt = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            # Just date
            dt = datetime.datetime.strptime(value, '%Y-%m-%d')
            
        return dt.strftime('%b %d, %Y')
    except (ValueError, TypeError):
        return str(value)

# Register Jinja filters
app.jinja_env.filters['format_date'] = format_date

# API Routes
@app.route('/')
def index():
    """Render the dashboard showing all debt entries and net balance."""
    db = get_db()
    
    # Get column names to check if created_at exists
    cursor = db.execute("PRAGMA table_info(debt)")
    columns = {row['name'] for row in cursor.fetchall()}
    
    # Use a safer query that works whether or not created_at exists
    if 'created_at' in columns:
        entries = db.execute('''
            SELECT *, 
                   CASE direction
                       WHEN 'they_owe' THEN amount
                       ELSE -amount
                   END as net_amount
            FROM debt 
            ORDER BY created_at DESC
        ''').fetchall()
    else:
        entries = db.execute('''
            SELECT *, 
                   CASE direction
                       WHEN 'they_owe' THEN amount
                       ELSE -amount
                   END as net_amount
            FROM debt 
            ORDER BY id DESC
        ''').fetchall()

    # Calculate statistics
    net_balance = sum(e['net_amount'] for e in entries)
    total_owed_to_you = sum(e['amount'] for e in entries if e['direction'] == 'they_owe')
    total_you_owe = sum(e['amount'] for e in entries if e['direction'] == 'you_owe')
    
    # Get unique people
    people = db.execute('SELECT DISTINCT person FROM debt ORDER BY person').fetchall()
    
    # Current datetime for templates
    current_year = datetime.datetime.now().year
    
    return render_template(
        'index.html',
        entries=entries,
        net_balance=net_balance,
        total_owed_to_you=total_owed_to_you,
        total_you_owe=total_you_owe,
        people=people,
        format_currency=format_currency,
        current_year=current_year
    )

@app.route('/add', methods=['POST'])
def add():
    """Add a new debt entry."""
    try:
        # Validate and extract form data
        person = request.form['person'].strip()
        if not person:
            flash("Person's name is required", "error")
            return redirect(url_for('index'))
            
        try:
            amount = float(request.form['amount'])
            if amount <= 0:
                flash("Amount must be positive", "error")
                return redirect(url_for('index'))
        except ValueError:
            flash("Invalid amount", "error")
            return redirect(url_for('index'))
            
        direction = request.form['direction']
        if direction not in ('you_owe', 'they_owe'):
            flash("Invalid direction", "error")
            return redirect(url_for('index'))
            
        note = request.form.get('note', '').strip()
        
        # Save to database
        db = get_db()
        
        # Format current time as YYYY-MM-DD HH:MM:SS for better SQLite compatibility
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # First check if the created_at column exists before inserting
        cursor = db.execute("PRAGMA table_info(debt)")
        columns = {row['name'] for row in cursor.fetchall()}
        
        if 'created_at' in columns and 'updated_at' in columns:
            db.execute(
                'INSERT INTO debt (person, amount, direction, note, created_at, updated_at) VALUES (?,?,?,?,?,?)',
                (person, amount, direction, note, now, now)
            )
        else:
            db.execute(
                'INSERT INTO debt (person, amount, direction, note) VALUES (?,?,?,?)',
                (person, amount, direction, note)
            )
        db.commit()
        
        flash(f"Debt record for {person} added successfully", "success")
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error(f"Error adding debt entry: {str(e)}")
        flash("An error occurred while adding the debt record", "error")
        return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """Delete a debt entry."""
    try:
        db = get_db()
        db.execute('DELETE FROM debt WHERE id = ?', (id,))
        db.commit()
        flash("Entry deleted successfully", "success")
    except Exception as e:
        app.logger.error(f"Error deleting debt entry: {str(e)}")
        flash("An error occurred while deleting the entry", "error")
        
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing debt entry."""
    db = get_db()
    
    if request.method == 'POST':
        try:
            # Validate and extract form data
            person = request.form['person'].strip()
            if not person:
                flash("Person's name is required", "error")
                return redirect(url_for('edit', id=id))
                
            try:
                amount = float(request.form['amount'])
                if amount <= 0:
                    flash("Amount must be positive", "error")
                    return redirect(url_for('edit', id=id))
            except ValueError:
                flash("Invalid amount", "error")
                return redirect(url_for('edit', id=id))
                
            direction = request.form['direction']
            if direction not in ('you_owe', 'they_owe'):
                flash("Invalid direction", "error")
                return redirect(url_for('edit', id=id))
                
            note = request.form.get('note', '').strip()
            
            # Format current time as YYYY-MM-DD HH:MM:SS for better SQLite compatibility
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # First check if the updated_at column exists before updating
            cursor = db.execute("PRAGMA table_info(debt)")
            columns = {row['name'] for row in cursor.fetchall()}
            
            # Update database
            if 'updated_at' in columns:
                db.execute(
                    'UPDATE debt SET person=?, amount=?, direction=?, note=?, updated_at=? WHERE id=?',
                    (person, amount, direction, note, now, id)
                )
            else:
                db.execute(
                    'UPDATE debt SET person=?, amount=?, direction=?, note=? WHERE id=?',
                    (person, amount, direction, note, id)
                )
            db.commit()
            
            flash("Entry updated successfully", "success")
            return redirect(url_for('index'))
            
        except Exception as e:
            app.logger.error(f"Error updating debt entry: {str(e)}")
            flash("An error occurred while updating the entry", "error")
            return redirect(url_for('edit', id=id))
    else:
        # GET request - show edit form
        entry = db.execute('SELECT * FROM debt WHERE id = ?', (id,)).fetchone()
        if entry:
            return render_template('edit.html', entry=entry)
        else:
            flash("Entry not found", "error")
            return redirect(url_for('index'))

@app.route('/api/summary')
def api_summary():
    """JSON API endpoint providing summary statistics."""
    from flask import jsonify
    
    db = get_db()
    entries = db.execute('''
        SELECT *, 
               CASE direction
                   WHEN 'they_owe' THEN amount
                   ELSE -amount
               END as net_amount
        FROM debt
    ''').fetchall()
    
    # Calculate statistics
    net_balance = sum(e['net_amount'] for e in entries)
    total_owed_to_you = sum(e['amount'] for e in entries if e['direction'] == 'they_owe')
    total_you_owe = sum(e['amount'] for e in entries if e['direction'] == 'you_owe')
    
    # Group by person
    people_summary = {}
    for entry in entries:
        person = entry['person']
        if person not in people_summary:
            people_summary[person] = 0
        people_summary[person] += entry['net_amount']
    
    return jsonify({
        'net_balance': net_balance,
        'total_owed_to_you': total_owed_to_you,
        'total_you_owe': total_you_owe,
        'people': [{'name': k, 'balance': v} for k, v in people_summary.items()]
    })

@app.route('/export', methods=['GET'])
def export_csv():
    """Export debt records as CSV."""
    import csv
    from io import StringIO
    from flask import Response
    
    db = get_db()
    
    # Get column names to check what fields exist
    cursor = db.execute("PRAGMA table_info(debt)")
    columns = {row['name'] for row in cursor.fetchall()}
    
    # Use a safer query that works whether or not created_at exists
    if 'created_at' in columns:
        entries = db.execute('SELECT * FROM debt ORDER BY created_at DESC').fetchall()
    else:
        entries = db.execute('SELECT * FROM debt ORDER BY id DESC').fetchall()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Determine available fields for the header and data rows
    header = ['ID', 'Person', 'Amount', 'Direction', 'Note']
    if 'created_at' in columns:
        header.append('Created At')
    if 'updated_at' in columns:
        header.append('Updated At')
    
    # Write header
    writer.writerow(header)
    
    # Write data rows
    for entry in entries:
        row = [
            entry['id'],
            entry['person'],
            entry['amount'],
            entry['direction'],
            entry.get('note', '')
        ]
        
        if 'created_at' in columns:
            row.append(entry.get('created_at', ''))
        if 'updated_at' in columns:
            row.append(entry.get('updated_at', ''))
        
        writer.writerow(row)
    
    # Create response
    response = Response(
        output.getvalue(), 
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment;filename=SettleSense_Export.csv'
        }
    )
    
    return response

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    current_year = datetime.datetime.now().year
    return render_template('error.html', error=e, current_year=current_year), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {str(e)}")
    current_year = datetime.datetime.now().year
    return render_template('error.html', error=e, current_year=current_year), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(host=host, port=port)
