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

# ---- Database Migration System ----
import os
import shutil
import sqlite3
import time

def check_database_status():
    """Check the database structure and return a list of checks."""
    db = get_db()
    cursor = db.execute("PRAGMA table_info(debt)")
    columns = {row['name'] for row in cursor.fetchall()}
    
    # Define required columns and checks
    required_columns = {
        'id', 'person', 'amount', 'direction', 'note', 
        'created_at', 'updated_at'
    }
    
    # Perform checks
    checks = [
        {
            'name': 'Table exists',
            'status': len(columns) > 0
        },
        {
            'name': 'Required columns',
            'status': required_columns.issubset(columns)
        }
    ]
    
    # Check if direction has proper constraint
    constraint_check = {'status': False, 'name': 'Direction constraint'}
    try:
        # Check if the constraint is defined properly
        table_info = db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='debt'").fetchone()
        if table_info and "CHECK(direction IN ('you_owe','they_owe'))" in table_info[0]:
            constraint_check['status'] = True
    except:
        pass
    
    checks.append(constraint_check)
    
    # Check for indexes (if we've added any)
    index_check = {'status': False, 'name': 'Person index'}
    try:
        indexes = db.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='debt'").fetchall()
        if any('person' in idx['name'] for idx in indexes):
            index_check['status'] = True
    except:
        pass
    
    checks.append(index_check)
    
    return checks

def needs_migration():
    """Determine if the database needs migration."""
    checks = check_database_status()
    return not all(check['status'] for check in checks)

def backup_database():
    """Create a backup of the current database."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    source = app.config['DATABASE']
    if os.path.exists(source):
        destination = os.path.join(backup_dir, f"debts_{timestamp}.sqlite")
        shutil.copy2(source, destination)
        return destination
    return None

@app.route('/migrate')
def migrate():
    """Show migration status page."""
    current_year = datetime.datetime.now().year
    db_checks = check_database_status()
    needs_mig = needs_migration()
    
    # Get user's theme preference from settings
    settings = get_settings()
    theme = settings.get('theme', 'light')
    
    return render_template(
        'migration.html',
        db_checks=db_checks,
        needs_migration=needs_mig,
        current_year=current_year,
        message=None,
        error=None,
        theme=theme
    )

@app.route('/migrate/run', methods=['POST'])
def run_migration():
    """Execute database migration."""
    error = None
    message = None
    error_details = None
    make_backup = request.form.get('backup', 'off') == 'on'
    
    try:
        if make_backup:
            backup_file = backup_database()
            if backup_file:
                message = f"Database backed up successfully."
        
        # Run a full migration
        db = get_db()
        
        # Get current columns
        cursor = db.execute("PRAGMA table_info(debt)")
        columns = {row['name'] for row in cursor.fetchall()}
        
        # Create temp table with new schema
        db.execute('''
        CREATE TABLE IF NOT EXISTS debt_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person TEXT NOT NULL,
            amount REAL NOT NULL,
            direction TEXT CHECK(direction IN ('you_owe','they_owe')) NOT NULL,
            note TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        ''')
        
        # Copy data from old to new table
        col_intersection = columns.intersection({'id', 'person', 'amount', 'direction', 'note', 'created_at', 'updated_at'})
        copy_cols = ', '.join(col_intersection)
        
        # Build placeholders for missing columns
        placeholders = []
        for col in {'id', 'person', 'amount', 'direction', 'note', 'created_at', 'updated_at'} - col_intersection:
            if col in ('created_at', 'updated_at'):
                placeholders.append(f"datetime('now') as {col}")
            elif col == 'note':
                placeholders.append("'' as note")
            
        placeholder_str = ', '.join(placeholders)
        
        if placeholder_str:
            select_stmt = f"SELECT {copy_cols}, {placeholder_str} FROM debt"
        else:
            select_stmt = f"SELECT {copy_cols} FROM debt"
            
        # Insert data into new table
        db.execute(f"INSERT INTO debt_new {select_stmt}")
        
        # Drop old table and rename new one
        db.execute("DROP TABLE debt")
        db.execute("ALTER TABLE debt_new RENAME TO debt")
        
        # Add indexes
        db.execute("CREATE INDEX IF NOT EXISTS idx_debt_person ON debt(person)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_debt_direction ON debt(direction)")
        
        # Update nulls with current date
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.execute("UPDATE debt SET created_at = ? WHERE created_at IS NULL", (now,))
        db.execute("UPDATE debt SET updated_at = ? WHERE updated_at IS NULL", (now,))
        
        db.commit()
        message = "Database migration completed successfully!"
        
    except Exception as e:
        error = "An error occurred during migration."
        error_details = str(e)
        app.logger.error(f"Migration error: {str(e)}")
        db.rollback()
    
    current_year = datetime.datetime.now().year
    db_checks = check_database_status()
    needs_mig = needs_migration()
    
    # Get user's theme preference from settings
    settings = get_settings()
    theme = settings.get('theme', 'light')
    
    return render_template(
        'migration.html',
        db_checks=db_checks,
        needs_migration=needs_mig,
        current_year=current_year,
        message=message,
        error=error,
        error_details=error_details,
        theme=theme
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
    # Get user's preferred currency symbol from settings
    settings = get_settings()
    symbol = settings.get('currency_symbol', '$')
    return f"{symbol}{abs(value):.2f}"

def format_date(value):
    """Format a date string nicely."""
    if not value:
        return "N/A"
        
    try:
        # Try different date formats
        if isinstance(value, datetime.datetime):
            dt = value
        elif 'T' in value:
            # ISO format with T separator
            dt = datetime.datetime.fromisoformat(value)
        elif ' ' in value:
            # SQLite format with space separator
            dt = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        else:
            # Just date
            dt = datetime.datetime.strptime(value, '%Y-%m-%d')
            
        # Get user's preferred date format from settings
        settings = get_settings()
        date_format = settings.get('date_format', 'YYYY-MM-DD')
        
        if date_format == 'MM/DD/YYYY':
            return dt.strftime('%m/%d/%Y')
        elif date_format == 'DD/MM/YYYY':
            return dt.strftime('%d/%m/%Y')
        else:  # YYYY-MM-DD
            return dt.strftime('%Y-%m-%d')
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
    
    # Extract search/filter parameters
    search_query = request.args.get('search', '').strip()
    filter_person = request.args.get('person', '').strip()
    filter_direction = request.args.get('direction', '').strip()
    sort_by = request.args.get('sort', 'date')
    sort_order = request.args.get('order', 'desc')
    
    # Build the base query
    base_query = '''
        SELECT *, 
               CASE direction
                   WHEN 'they_owe' THEN amount
                   ELSE -amount
               END as net_amount
        FROM debt 
        WHERE 1=1
    '''
    
    query_params = []
    
    # Apply filters
    if search_query:
        base_query += " AND (person LIKE ? OR note LIKE ?)"
        query_params.extend(['%' + search_query + '%', '%' + search_query + '%'])
    
    if filter_person:
        base_query += " AND person = ?"
        query_params.append(filter_person)
    
    if filter_direction:
        base_query += " AND direction = ?"
        query_params.append(filter_direction)
    
    # Apply sorting
    if sort_by == 'amount':
        base_query += " ORDER BY amount"
    elif sort_by == 'person':
        base_query += " ORDER BY person"
    elif sort_by == 'direction':
        base_query += " ORDER BY direction"
    else:  # Default: date or fallback to id
        if 'created_at' in columns:
            base_query += " ORDER BY created_at"
        else:
            base_query += " ORDER BY id"
    
    base_query += " " + sort_order.upper()
    
    # Execute query
    entries = db.execute(base_query, query_params).fetchall()

    # Calculate statistics
    net_balance = sum(e['net_amount'] for e in entries)
    total_owed_to_you = sum(e['amount'] for e in entries if e['direction'] == 'they_owe')
    total_you_owe = sum(e['amount'] for e in entries if e['direction'] == 'you_owe')
    
    # Get unique people for filter dropdown
    people = db.execute('SELECT DISTINCT person FROM debt ORDER BY person').fetchall()
    
    # Get person summary for charts
    people_summary = []
    person_balances = {}
    
    for entry in entries:
        person = entry['person']
        if person not in person_balances:
            person_balances[person] = 0
        
        if entry['direction'] == 'they_owe':
            person_balances[person] += entry['amount']
        else:
            person_balances[person] -= entry['amount']
    
    for person, balance in person_balances.items():
        people_summary.append({
            'name': person,
            'balance': balance
        })
    
    # Sort by balance (highest positive first)
    people_summary.sort(key=lambda x: x['balance'], reverse=True)
    
    # Get user's theme preference from settings
    settings = get_settings()
    theme = settings.get('theme', 'light')
    
    # Current datetime for templates
    current_year = datetime.datetime.now().year
    
    # Keep track of current filters for form
    current_filters = {
        'search': search_query,
        'person': filter_person,
        'direction': filter_direction,
        'sort': sort_by,
        'order': sort_order
    }
    
    return render_template(
        'index.html',
        entries=entries,
        net_balance=net_balance,
        total_owed_to_you=total_owed_to_you,
        total_you_owe=total_you_owe,
        people=people,
        people_summary=people_summary,
        format_currency=format_currency,
        current_year=current_year,
        filters=current_filters,
        theme=theme
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
            # Get user's theme preference from settings
            settings = get_settings()
            theme = settings.get('theme', 'light')
            return render_template('edit.html', entry=entry, theme=theme)
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

# ---- Settings Management ----
import json
import platform
import flask

def get_settings():
    """Load application settings from JSON file."""
    settings_path = os.path.join(BASE_DIR, 'instance', 'settings.json')
    if os.path.exists(settings_path):
        try:
            with open(settings_path, 'r') as f:
                return json.load(f)
        except:
            app.logger.warning("Failed to load settings.json, using defaults")
    return {}

def save_settings(settings):
    """Save application settings to JSON file."""
    settings_path = os.path.join(BASE_DIR, 'instance', 'settings.json')
    os.makedirs(os.path.dirname(settings_path), exist_ok=True)
    try:
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        app.logger.error(f"Failed to save settings: {str(e)}")
        return False

def get_system_info():
    """Get system information for the About page."""
    return {
        'python_version': platform.python_version(),
        'flask_version': flask.__version__,
        'sqlite_version': sqlite3.sqlite_version,
        'os': f"{platform.system()} {platform.release()}"
    }

def get_db_info():
    """Get database information for the Settings page."""
    db_path = app.config['DATABASE']
    
    if not os.path.exists(db_path):
        return {
            'path': db_path,
            'size': '0 KB',
            'modified': None,
            'record_count': 0
        }
    
    # Get database size in KB
    size_bytes = os.path.getsize(db_path)
    if size_bytes < 1024:
        size_str = f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    
    # Get modification time
    mtime = os.path.getmtime(db_path)
    modified = datetime.datetime.fromtimestamp(mtime)
    
    # Get record count
    db = get_db()
    try:
        count = db.execute("SELECT COUNT(*) FROM debt").fetchone()[0]
    except:
        count = 0
        
    return {
        'path': db_path,
        'size': size_str,
        'modified': modified,
        'record_count': count
    }

def get_backups():
    """Get list of available backups."""
    backup_dir = os.path.join(BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        return []
    
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.sqlite'):
            file_path = os.path.join(backup_dir, filename)
            
            # Get size
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
            
            # Get creation time
            ctime = os.path.getctime(file_path)
            created = datetime.datetime.fromtimestamp(ctime)
            
            backups.append({
                'name': filename,
                'file': file_path,
                'size': size_str,
                'created': created
            })
    
    # Sort by creation time, newest first
    backups.sort(key=lambda x: x['created'], reverse=True)
    return backups

@app.route('/settings')
def settings():
    """Render the settings page."""
    current_settings = get_settings()
    db_info = get_db_info()
    sys_info = get_system_info()
    backups = get_backups()
    current_year = datetime.datetime.now().year
    
    # Get the current theme
    theme = current_settings.get('theme', 'light')
    
    return render_template(
        'settings.html',
        settings=current_settings,
        db_path=db_info['path'],
        db_size=db_info['size'],
        db_modified=db_info['modified'],
        record_count=db_info['record_count'],
        sys_info=sys_info,
        backups=backups,
        current_year=current_year,
        theme=theme
    )

@app.route('/settings/update', methods=['POST'])
def update_settings():
    """Update application settings."""
    section = request.form.get('section', '')
    current_settings = get_settings()
    
    if section == 'general':
        current_settings['currency_symbol'] = request.form.get('currency_symbol', '$')
        current_settings['date_format'] = request.form.get('date_format', 'YYYY-MM-DD')
    
    elif section == 'display':
        current_settings['theme'] = request.form.get('theme', 'light')
        current_settings['records_per_page'] = request.form.get('records_per_page', '10')
        current_settings['show_charts'] = 'true' if request.form.get('show_charts') else 'false'
    
    if save_settings(current_settings):
        flash(f"Settings updated successfully", "success")
    else:
        flash("Failed to save settings", "error")
    
    return redirect(url_for('settings') + f"#{section}")

@app.route('/backup/create', methods=['POST'])
def create_backup():
    """Create a new database backup."""
    backup_file = backup_database()
    
    if backup_file:
        flash(f"Backup created successfully: {os.path.basename(backup_file)}", "success")
    else:
        flash("Failed to create backup", "error")
    
    return redirect(url_for('settings') + "#backup")

@app.route('/backup/restore', methods=['POST'])
def restore_backup():
    """Restore database from backup."""
    backup_file = request.form.get('file', '')
    
    if not backup_file or not os.path.exists(backup_file):
        flash("Invalid backup file", "error")
        return redirect(url_for('settings') + "#backup")
    
    try:
        # Close current database connection
        db = getattr(g, '_database', None)
        if db:
            db.close()
            g._database = None
        
        # Create a backup of current database before restoring
        current_backup = backup_database()
        
        # Replace database with backup
        shutil.copy2(backup_file, app.config['DATABASE'])
        
        flash("Backup restored successfully", "success")
    except Exception as e:
        app.logger.error(f"Failed to restore backup: {str(e)}")
        flash(f"Failed to restore backup: {str(e)}", "error")
    
    return redirect(url_for('settings') + "#backup")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    current_year = datetime.datetime.now().year
    # Get user's theme preference from settings
    settings = get_settings()
    theme = settings.get('theme', 'light')
    return render_template('error.html', error=e, current_year=current_year, theme=theme), 404

@app.errorhandler(500)
def server_error(e):
    app.logger.error(f"Server error: {str(e)}")
    current_year = datetime.datetime.now().year
    # Get user's theme preference from settings
    settings = get_settings()
    theme = settings.get('theme', 'light')
    return render_template('error.html', error=e, current_year=current_year, theme=theme), 500

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    app.run(host=host, port=port)
