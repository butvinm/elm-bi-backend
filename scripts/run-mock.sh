#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
source venv/bin/activate

# Ensure pip is up-to-date
pip install --upgrade pip

# Install FastAPI if not already installed
pip show fastapi &> /dev/null
if [ $? -ne 0 ]; then
    echo "FastAPI not found. Installing..."
    pip install fastapi uvicorn
    echo "FastAPI installed."
else
    echo "FastAPI is already installed."
fi

# Run the FastAPI server
uvicorn mock.main:app --port 6969 --reload
