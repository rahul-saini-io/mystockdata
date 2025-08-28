# Stock Transaction Manager

A modern web application for managing stock transactions with comprehensive portfolio tracking, data visualization, and export functionality - designed for local development and personal use.

## Features

### 📊 Core Functionality
- **Stock Transaction Management**: Record buy/sell transactions with automatic calculations
- **Interactive DataTables**: Sortable, searchable transactions with pagination
- **Real-time Validation**: Client and server-side validation with user feedback
- **Bulk CSV Import**: Upload multiple transactions via CSV with error reporting
- **Dashboard Analytics**: Clean portfolio overview with key metrics

### 🧮 Automatic Calculations
- **Total Cost**: Buy quantity × Buy price per stock
- **Total Selling Cost**: Sell quantity × Sell price per stock  
- **Remaining Quantity**: Buy quantity - Sell quantity
- **Profit/Loss %**: Accurate calculation based on proportional costs
- **Holding Days**: Fixed calculation that stops counting after sell date

### 📈 Data Visualization
- **Portfolio Distribution**: Interactive doughnut chart of current holdings
- **Key Statistics**: Total investment, returns, profit/loss, active stocks
- **Additional Metrics**: Average P/L, total shares, profitable stocks count

### 📁 Export Options
- **CSV Export**: Download all transactions with complete data
- **Excel Export**: Formatted spreadsheet with all calculated fields
- **Sample CSV**: Download template for bulk import

## Technology Stack

### Backend
- **Flask** - Lightweight web framework
- **SQLAlchemy** - Database ORM with automatic relationships
- **MySQL** - Reliable database for transaction storage
- **Pandas** - Data processing for exports and imports

### Frontend
- **Bootstrap 5** - Modern responsive UI framework
- **jQuery** - JavaScript functionality and AJAX
- **DataTables** - Advanced table features with server-side processing
- **Chart.js** - Interactive portfolio visualization
- **Font Awesome** - Professional icons

## Quick Start

### Prerequisites
- **Python 3.8+**
- **MySQL 5.7+** (or MariaDB)
- **Git** (optional)

### Installation Steps

1. **Clone/Download the project**
```bash
# Option 1: Clone with Git
git clone https://github.com/rahul-saini-io/mystockdata.git
cd mystockdata

# Option 2: Download and extract ZIP from GitHub
# https://github.com/rahul-saini-io/mystockdata/archive/refs/heads/main.zip
# Extract to your preferred directory
cd mystockdata
```

2. **Set up Python environment**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

3. **Set up MySQL database**
```sql
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE mystocktrading CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit
```

4. **Configure database connection**
```python
# Edit config.py if needed (default settings work for local MySQL)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/mystocktrading'
```

5. **Initialize database and run**
```bash
# Start the application (will create tables automatically)
python app.py
```

6. **Open in browser**
```
http://localhost:5000
```

## Project Structure

```
mystockdata/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models.py                # Database models with auto-calculations
│   ├── routes.py                # API routes and bulk import
│   ├── static/
│   │   └── js/
│   │       ├── transactions.js  # Transaction management + bulk import
│   │       └── dashboard.js     # Clean dashboard functionality
│   └── templates/
│       ├── base.html            # Base template with Bootstrap 5
│       ├── index.html           # Transactions page with bulk import
│       └── dashboard.html       # Optimized dashboard layout
├── config.py                    # Configuration settings
├── requirements.txt             # Python dependencies
├── app.py                       # Application entry point
├── run.bat                      # Windows batch file to start app
├── sample_transactions.csv      # Sample CSV for testing bulk import
└── README.md                    # This file
```

## Key Features Guide

### 🔄 Bulk CSV Import
1. Click **"Bulk Import"** → **"Download Sample CSV"**
2. Fill in your transaction data using the template
3. Click **"Upload CSV"** and select your file
4. Review import results with detailed error reporting

**CSV Format:**
```csv
stock_name,buy_quantity,buy_price_per_stock,buy_date,sell_quantity,sell_price_per_stock,sell_date
RELIANCE,10,2500.50,2024-01-15,5,2650.75,2024-02-20
TCS,25,3200.00,2024-01-10,0,0,
```

### 📊 Dashboard Overview
- **Stats Cards**: Total transactions, investment, returns, net P/L
- **Portfolio Chart**: Visual distribution of your current holdings
- **Additional Stats**: Active stocks, average P/L, total shares, profitable stocks

### ✏️ Transaction Management
- **Add**: Click "Add Transaction" for the guided form
- **Edit**: Click the pencil icon on any transaction
- **Delete**: Click trash icon with confirmation dialog
- **Search**: Use the search box to filter by stock name
- **Sort**: Click any column header to sort data

## API Endpoints

### Transaction Management
- `GET /api/transactions` - List transactions with pagination/search
- `POST /api/transactions` - Create new transaction
- `GET /api/transactions/<id>` - Get specific transaction
- `PUT /api/transactions/<id>` - Update transaction
- `DELETE /api/transactions/<id>` - Delete transaction

### Bulk Operations & Export
- `GET /api/sample-csv` - Download CSV template
- `POST /api/bulk-import` - Upload and process CSV file
- `GET /api/export/csv` - Export all data as CSV
- `GET /api/export/excel` - Export all data as Excel

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics

## Database Schema

The application uses a single optimized table with automatic calculations:

```sql
CREATE TABLE stock_transactions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    stock_name VARCHAR(100) NOT NULL,
    buy_quantity INT NOT NULL,
    buy_price_per_stock DECIMAL(10,4) NOT NULL,
    total_cost DECIMAL(15,4) NOT NULL,
    buy_date DATE NOT NULL,
    sell_quantity INT DEFAULT 0,
    sell_price_per_stock DECIMAL(10,4) DEFAULT 0,
    total_selling_cost DECIMAL(15,4) DEFAULT 0,
    sell_date DATE,
    remaining_quantity INT NOT NULL,
    profit_loss_percentage DECIMAL(10,4) DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stock_name (stock_name),
    INDEX idx_buy_date (buy_date),
    INDEX idx_created_at (created_at)
);
```

## Configuration

### Database Settings (config.py)
```python
class Config:
    SECRET_KEY = 'dev-secret-key-for-local-development'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/mystocktrading'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### Environment Variables (Optional)
Create `.env` file for custom settings:
```env
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/mystocktrading
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check if MySQL is running
# Windows: Check Services or run:
net start mysql80

# Verify database exists
mysql -u root -e "SHOW DATABASES;"
```

**2. Module Not Found Error**
```bash
# Ensure virtual environment is activated
.venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt
```

**3. DataTables Ajax Error**
- Ensure Flask app is running on port 5000
- Check browser console for detailed errors
- Verify `/api/transactions` endpoint is accessible

**4. CSV Import Issues**
- Use the exact column names from sample CSV
- Check date format (YYYY-MM-DD)
- Ensure numeric fields contain valid numbers
- Review error messages in import results

### Development Tips

- **Debug Mode**: App runs in debug mode by default for development
- **Console Logs**: Check browser console for JavaScript errors
- **Network Tab**: Monitor API calls in browser developer tools
- **Database**: Use MySQL Workbench or phpMyAdmin for database inspection

## Sample Data

The project includes `sample_transactions.csv` with 10 example transactions covering various scenarios:
- Partial stock sales
- Complete stock sales  
- Stocks held without selling
- Different stock types and price ranges

## Security Notes

For local development, the app uses basic security:
- Input validation on both client and server
- SQL injection prevention via SQLAlchemy ORM  
- CSRF protection can be added with Flask-WTF if needed
- Debug mode should only be used locally

## Support

For issues or questions:
1. Check this README and troubleshooting section
2. Review browser console for JavaScript errors
3. Check Flask console output for server errors
4. Verify database connection and table structure

## License

This project is intended for personal/educational use. Feel free to modify and adapt for your needs.