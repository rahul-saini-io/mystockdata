#!/bin/bash

echo "========================================"
echo "  Stock Transaction Manager - Local Dev"
echo "========================================"
echo

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$1/4]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

print_error() {
    echo -e "${RED}ERROR:${NC} $1"
    exit 1
}

# Check Python installation
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        print_error "Python is not installed or not in PATH!"
        echo "Please install Python 3.8+ from https://python.org"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1-2)
if [[ "$(printf '%s\n' "3.8" "$PYTHON_VERSION" | sort -V | head -n1)" != "3.8" ]]; then
    print_error "Python 3.8+ is required. Found version $PYTHON_VERSION"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_status 1 "Creating virtual environment..."
    $PYTHON_CMD -m venv .venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment!"
    fi
else
    print_status 1 "Virtual environment already exists $(print_success "")"
fi

# Activate virtual environment
print_status 2 "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Failed to activate virtual environment!"
fi

# Install/update dependencies
print_status 3 "Installing dependencies..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies!"
fi

# Check MySQL installation
print_status 4 "Checking MySQL connection..."
if ! command -v mysql &> /dev/null; then
    print_warning "MySQL not found in PATH. Make sure MySQL is running."
    echo "  - macOS: brew services start mysql"
    echo "  - Linux: sudo systemctl start mysql"
else
    print_success "MySQL found in PATH"
fi

echo
echo "========================================"
echo -e "  ${GREEN}🚀 STARTING APPLICATION${NC}"
echo "========================================"
echo
echo -e "${BLUE}→${NC} Local URL: http://localhost:5000"
echo -e "${BLUE}→${NC} Dashboard: http://localhost:5000/dashboard"
echo -e "${BLUE}→${NC} Press Ctrl+C to stop the server"
echo -e "${BLUE}→${NC} Database will be created automatically"
echo

# Start the application
$PYTHON_CMD app.py

echo
echo "Application stopped."