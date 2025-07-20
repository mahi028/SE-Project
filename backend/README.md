# EZCare Backend

This backend application currently **only supports Linux environments**.

## Prerequisites

Before running the backend application, you need to install the following dependencies:

```sh
sudo apt install cmake
python3 -m pip install --upgrade pip setuptools wheel
```

## Setup and Installation

1. Unzip and Navigate to the backend directory:
```sh
cd backend
```

2. Create and Activate Virtual Environment (Optional):
```sh
python3 -m venv env
source env/bin/activate
```

3. Install Python dependencies:
```sh
pip install -r requirements.txt
```

## Running the Application

To start the backend server:

```sh
python3 app.py
```

## Environment Requirements

- **Operating System**: Linux (Ubuntu/Debian recommended)
- **Python**: 3.7 or higher
- **CMake**: Required for certain Python packages

## Notes

- Make sure all prerequisites are installed before attempting to run the application
- The application may not work properly on Windows or macOS due to Linux-specific dependencies
- If you encounter any installation issues, ensure your system is up to date: `sudo apt update && sudo apt upgrade`