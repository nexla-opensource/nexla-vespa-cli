#!/bin/bash
# Vespa Nexla Plugin CLI - Unix Version (Linux/macOS)

set -e  # Exit on any error

echo "Starting Vespa Nexla Plugin..."

# Function to install Python on different systems
install_python() {
    echo "Python not found. Attempting to install..."

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew >/dev/null 2>&1; then
            echo "Installing Python via Homebrew..."
            brew install python3
        else
            echo "Please install Homebrew first: https://brew.sh/"
            echo "Or download Python from: https://www.python.org/downloads/"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get >/dev/null 2>&1; then
            echo "Installing Python via apt..."
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif command -v yum >/dev/null 2>&1; then
            echo "Installing Python via yum..."
            sudo yum install -y python3 python3-pip
        elif command -v dnf >/dev/null 2>&1; then
            echo "Installing Python via dnf..."
            sudo dnf install -y python3 python3-pip
        elif command -v pacman >/dev/null 2>&1; then
            echo "Installing Python via pacman..."
            sudo pacman -S python python-pip
        else
            echo "Could not detect package manager. Please install Python manually:"
            echo "https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "Unsupported operating system. Please install Python manually:"
        echo "https://www.python.org/downloads/"
        exit 1
    fi
}

# Check if Python is installed
if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    install_python
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python"
fi

# Check if we're in the correct directory
if [[ ! -f "main.py" ]]; then
    echo "Error: main.py not found. Please run this script from the plugin directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [[ ! -d ".venv" ]]; then
    echo "Creating Python virtual environment..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade pip
echo "Updating pip..."
python -m pip install --upgrade pip

# Install requirements
if [[ -f "requirements.txt" ]]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Some dependencies may be missing."
fi

# Run the main application
echo ""
echo "==========================================="
echo "    Welcome to Vespa Nexla Plugin CLI"
echo "==========================================="
echo ""

python main.py

# Deactivate virtual environment
deactivate