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

SettleSense is a professional-grade web application designed to track peer-to-peer debts and credits. It provides a clean, intuitive interface for users to log financial transactions, view their net balance, and manage settlements with precision.

## Features

- **💰 Comprehensive Debt Tracking**: Log debts and credits with detailed information
- **📊 Advanced Analytics Dashboard**: Visual representations of your financial situation
- **⏱️ Time-Based Insights**: Track when debts were created and modified
- **🔄 Intuitive Transaction Management**: Add, edit, and delete entries with ease
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🔍 Search & Filter**: Find specific transactions quickly
- **📁 Data Export**: Export your debt records in CSV format
- **🔧 Database Migration System**: Seamlessly upgrade between versions
- **⚙️ Customizable Settings**: Personalize your experience with currency symbols, date formats, and themes
- **💾 Backup & Restore**: Protect your financial data
- **🌓 Dark Mode**: Reduce eye strain with a professional dark theme

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Quick Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/SettleSense.git
   cd SettleSense
   ```

2. Run the installation script:
   ```sh
   chmod +x install.sh
   ./install.sh
   ```

3. Start the application:
   ```sh
   ./run.sh
   ```

### Manual Setup
1. Clone the repository and navigate to the project folder
2. Create a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r settle_sense/requirements.txt
   ```
4. Run the application:
   ```sh
   python -m settle_sense.app
   ```

## Usage

### Adding Debt Entries
1. Navigate to the dashboard
2. Fill out the "New Debt Entry" form
3. Select the direction (They Owe You / You Owe Them)
4. Add an optional note for context
5. Click "Save Entry"

### Managing Entries
- **Edit**: Click the pencil icon to modify an entry
- **Delete**: Click the trash icon and confirm deletion
- **Search & Filter**: Use the search bar to find entries by name or note
- **Sort**: Click column headers to sort by different fields

### Data Visualization
The application provides visual insights through:
- Balance pie chart showing debts vs. credits
- Person-specific bar charts showing individual balances

### Settings & Preferences
Access the settings page to:
- Change currency symbol
- Select date format
- Toggle between light and dark themes
- Set display options
- Manage database backups

## Development

### Project Structure
```
SettleSense/
├── settle_sense/             # Main application
│   ├── app.py                # Flask application
│   ├── requirements.txt      # Python dependencies
│   ├── static/               # Static assets
│   │   ├── logo.png
│   │   ├── script.js
│   │   └── style.css
│   ├── templates/            # HTML templates
│   │   ├── edit.html
│   │   ├── error.html
│   │   ├── index.html
│   │   ├── migration.html
│   │   └── settings.html
│   └── instance/             # Instance-specific data
│       ├── debts.sqlite      # SQLite database
│       └── settings.json     # User settings
├── backups/                  # Database backups
├── install.sh                # Installation script
├── run.sh                    # Start script
└── service.sh                # Service management
```

### Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
