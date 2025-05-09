#!/bin/bash
# Run script for SettleSense application

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r settle_sense/requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Change to the application directory
cd settle_sense

# Run the Flask application
echo "Starting SettleSense..."
python app.py

# Exit with the same status code as the Flask app
exit $?
