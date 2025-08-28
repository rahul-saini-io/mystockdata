# Stock Transaction Manager - Local Development Setup

This guide focuses on setting up the application for **local development and personal use only**. No production deployment instructions are included.

## 🚀 Quick Start

### Windows (Automated Setup)
1. **Double-click `run.bat`** - This will automatically:
   - Check Python installation
   - Create virtual environment
   - Install dependencies  
   - Check MySQL connection
   - Start the application
2. **Open browser** to `http://localhost:5000`

### Mac/Linux (Automated Setup)
1. **Open Terminal** and navigate to project folder
2. **Run the script**: `./run.sh`
   - If permission denied: `chmod +x run.sh && ./run.sh`
3. **Open browser** to `http://localhost:5000`

### Manual Setup
Follow the detailed instructions below for more control.

## 📋 Prerequisites

Before starting, ensure you have:

### Required Software
- **Python 3.8+** - [Download from python.org](https://www.python.org/downloads/)
- **MySQL 5.7+** or **MariaDB** - [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **Git** (optional) - [Download Git](https://git-scm.com/downloads)

### Check Installation
```bash
# Verify Python (should show 3.8 or higher)
python --version

# Verify MySQL is running
mysql --version
```

## 🔧 Manual Setup Steps

### 1. Get the Project
```bash
# Option A: Clone with Git
git clone https://github.com/rahul-saini-io/mystockdata.git
cd mystockdata

# Option B: Download ZIP from GitHub
# Go to: https://github.com/rahul-saini-io/mystockdata
# Click "Code" → "Download ZIP"
# Extract and navigate to the folder in command prompt
cd mystockdata
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# You should see (.venv) in your command prompt

# Install all dependencies
pip install -r requirements.txt
```

### 3. Set Up MySQL Database
```sql
# Open MySQL Command Line Client or MySQL Workbench
# Connect with your MySQL root user

# Create the database
CREATE DATABASE mystocktrading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Exit MySQL
exit
```

### 4. Configure Database Connection (If Needed)
The app uses these default settings (edit `config.py` if different):
```python
# Default database settings (usually work for local MySQL)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/mystocktrading'

# This means:
# - Username: root
# - Password: (empty)
# - Host: localhost  
# - Port: 3306
# - Database: mystocktrading
```

### 5. Start the Application
```bash
# Make sure virtual environment is activated
# You should see (.venv) in command prompt

# Start the app (creates tables automatically)
python app.py

# You should see:
# * Running on http://127.0.0.1:5000
# * Debug mode: on
```

### 6. Access the Application
Open your browser and go to: `http://localhost:5000`

## 🗂️ Project Structure

After setup, your project should look like this:
```
mystockdata/
├── .venv/                           # Virtual environment (auto-created)
├── app/
│   ├── __init__.py                  # Flask app factory
│   ├── models.py                    # Database models
│   ├── routes.py                    # All API routes
│   ├── static/js/
│   │   ├── dashboard.js             # Dashboard functionality
│   │   └── transactions.js          # Transaction management + bulk import
│   └── templates/
│       ├── base.html                # Base template
│       ├── dashboard.html           # Dashboard page
│       └── index.html               # Transactions page
├── config.py                        # Configuration settings
├── requirements.txt                 # Python dependencies
├── app.py                           # Application entry point
├── run.bat                          # Windows startup script (double-click to run)
├── run.sh                           # Mac/Linux startup script (./run.sh)
├── sample_transactions.csv          # Sample data for bulk import
├── README.md                        # Full documentation
└── SETUP.md                         # This file
```

## ✨ Testing the Setup

### 1. Test Basic Functionality
- ✅ Dashboard loads at `http://localhost:5000/dashboard`
- ✅ Transactions page at `http://localhost:5000`
- ✅ Add a test transaction using the "Add Transaction" button
- ✅ Try the bulk CSV import with the provided sample file

### 2. Test CSV Import
1. Go to transactions page
2. Click **"Bulk Import"** → **"Download Sample CSV"**
3. Open the downloaded file, review the format
4. Click **"Upload CSV"** and select `sample_transactions.csv` 
5. Verify 10 transactions are imported successfully

### 3. Test Dashboard
- Navigate to dashboard to see charts and statistics
- Verify data from imported transactions appears correctly

## 🔍 Troubleshooting

### Common Issues & Solutions

#### ❌ Database Connection Error
```
Error: Can't connect to MySQL server
```
**Solutions:**
```bash
# 1. Check if MySQL is running
# Windows: Open Services and look for MySQL80
# Or start it manually:
net start mysql80

# 2. Test MySQL connection manually
mysql -u root -p
# Enter your MySQL password (or just press Enter if no password)

# 3. Verify database exists
mysql -u root -e "SHOW DATABASES;" | grep mystocktrading
```

#### ❌ Module Not Found Error
```
ModuleNotFoundError: No module named 'flask'
```
**Solutions:**
```bash
# 1. Ensure virtual environment is activated
# You should see (.venv) in command prompt
.venv\Scripts\activate

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Check Python version
python --version  # Should be 3.8+
```

#### ❌ Port Already in Use
```
Address already in use: Port 5000
```
**Solutions:**
```bash
# 1. Find what's using port 5000
netstat -ano | findstr :5000

# 2. Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# 3. Or run on different port
python app.py --port 5001
```

#### ❌ DataTables Ajax Error
```
DataTables warning: Ajax error
```
**Solutions:**
1. Ensure Flask app is running on port 5000
2. Check browser console (F12) for detailed errors
3. Verify `http://localhost:5000/api/transactions` loads in browser
4. Check if database connection is working

#### ❌ CSV Import Issues
**Common Problems:**
- Wrong column names → Use exact headers from sample CSV
- Date format errors → Use YYYY-MM-DD format
- Number format → Use numbers without currency symbols
- Empty required fields → Fill in all required columns

**Solutions:**
1. Download and examine the sample CSV file
2. Use the exact column headers shown
3. Check error messages in the import results dialog

### 🛠️ Development Tips

#### Enable Detailed Logging
```python
# Edit app.py to see more detailed output
import logging
logging.basicConfig(level=logging.DEBUG)
```

#### Reset Database (If Needed)
```bash
# If you need to start fresh
mysql -u root -e "DROP DATABASE mystocktrading; CREATE DATABASE mystocktrading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Then restart the app to recreate tables
python app.py
```

#### Check API Endpoints
```bash
# Test API endpoints manually
# 1. Get all transactions
curl http://localhost:5000/api/transactions

# 2. Test dashboard stats
curl http://localhost:5000/api/dashboard/stats
```

#### Browser Developer Tools
- **F12** → **Console tab**: Check for JavaScript errors
- **Network tab**: Monitor API calls and responses  
- **Elements tab**: Inspect HTML and CSS issues

## 📊 Using the Application

### Dashboard Features
- **Portfolio Overview**: Total investment, returns, profit/loss
- **Active Holdings**: Chart showing your current stock distribution  
- **Key Metrics**: Summary statistics about your portfolio

### Transaction Management
- **Add Transactions**: Record individual buy/sell transactions
- **Bulk Import**: Upload many transactions via CSV file
- **Edit/Delete**: Modify existing transactions as needed
- **Search/Sort**: Find specific transactions quickly

### Export Options
- **CSV Export**: Download all data for Excel/analysis
- **Excel Export**: Formatted spreadsheet with all calculations

## 🔒 Security for Local Use

Since this is for local development only:
- ✅ Debug mode is enabled for easier troubleshooting
- ✅ No external network access required
- ✅ MySQL can use simple local configuration
- ✅ No HTTPS setup needed for localhost

**Keep in mind:**
- This setup is **NOT suitable for internet deployment**
- Database has minimal security (OK for local use)
- Debug mode shows detailed errors (helpful for development)

## 📞 Getting Help

If you encounter issues:

1. **Check this guide first** - Most common issues are covered above
2. **Check browser console** - F12 → Console tab for JavaScript errors  
3. **Check Flask output** - Look at the command prompt where you ran `python app.py`
4. **Check database** - Verify MySQL is running and database exists
5. **Try sample data** - Use the provided CSV file to test bulk import

### Useful Commands for Debugging
```bash
# Check if app is responding
curl http://localhost:5000

# Check database connection
mysql -u root -e "USE mystocktrading; SHOW TABLES;"

# Check Python environment
pip list | grep -i flask

# Restart everything fresh
# 1. Close app (Ctrl+C)
# 2. Restart MySQL service
# 3. Run: python app.py
```

Remember: This is designed for **local development only** - perfect for learning, testing, or personal portfolio tracking on your own computer!