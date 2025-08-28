@echo off
echo Starting Stock Transaction Manager...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Set Flask environment
set FLASK_APP=app.py
set FLASK_ENV=development

REM Initialize database if needed
echo Initializing database...
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Database initialized!')"

echo.
echo Starting Flask application...
echo Access the application at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python app.py
pause