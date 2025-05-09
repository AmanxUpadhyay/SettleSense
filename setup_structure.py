import os

# Base project directory
base = 'settle_sense'

# Folders to create under base
dirs = [
    base,
    os.path.join(base, 'templates'),
    os.path.join(base, 'static'),
    os.path.join(base, 'instance'),
]

# Files to touch
files = [
    os.path.join(base, 'app.py'),
    os.path.join(base, 'requirements.txt'),
    os.path.join(base, 'templates', 'index.html'),
    os.path.join(base, 'static', 'style.css'),
    os.path.join(base, 'instance', 'debts.sqlite'),
]

# Create directories
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Create empty files
for f in files:
    open(f, 'a').close()

print(f"Created project structure under ./{base}/")