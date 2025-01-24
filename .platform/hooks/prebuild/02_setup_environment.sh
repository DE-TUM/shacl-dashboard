#!/bin/bash

# echo "Starting environment setup..."

# # Exit on any error
# set -e

# # Check if Node.js and npm are installed
# if ! command -v npm &> /dev/null; then
#     echo "npm is not installed. Please ensure Node.js and npm are installed before running this script."
#     exit 1
# fi

# # Install global Node.js dependencies
# echo "Installing global Node.js dependencies..."
# if ! command -v vue &> /dev/null; then
#     echo "Vue CLI not found. Installing..."
#     if ! sudo npm install -g @vue/cli; then
#         echo "Failed to install Vue CLI. Exiting."
#         exit 1
#     fi
# else
#     echo "Vue CLI is already installed."
# fi

# # Set project directory
# PROJECT_DIR="/var/app/staging"

# # Validate project directory
# if [ ! -d "$PROJECT_DIR" ]; then
#     echo "Project directory $PROJECT_DIR not found. Exiting."
#     exit 1
# fi

# # Navigate to project directory
# cd "$PROJECT_DIR" || { echo "Failed to navigate to $PROJECT_DIR. Exiting."; exit 1; }

# # Remove existing package-lock.json to ensure fresh dependency installation
# if [ -f "package-lock.json" ]; then
#     echo "Removing existing package-lock.json..."
#     rm -f package-lock.json || { echo "Failed to remove package-lock.json. Exiting."; exit 1; }
# fi

# # Install project-specific Node.js dependencies
# echo "Installing project-specific Node.js dependencies..."
# if [ -f "package.json" ]; then
#     echo "Running npm install..."
#     if ! npm install; then
#         echo "npm install failed. Exiting."
#         exit 1
#     fi
# else
#     echo "No package.json found. Skipping Node.js dependency installation."
# fi

# # Build Vue app
# echo "Building Vue app..."
# if [ -f "package.json" ] && grep -q '"build":' package.json; then
#     echo "Running npm run build..."
#     if ! npm run build; then
#         echo "Vue app build failed. Exiting."
#         exit 1
#     fi
# else
#     echo "Build script not found in package.json. Skipping Vue app build."
# fi

# # Set Python service directory
# PYTHON_SERVICE_DIR="/var/app/staging/src/service"

# # Validate Python service directory
# if [ ! -d "$PYTHON_SERVICE_DIR" ]; then
#     echo "Python service directory $PYTHON_SERVICE_DIR not found. Exiting."
#     exit 1
# fi

# # Navigate to Python service directory
# cd "$PYTHON_SERVICE_DIR" || { echo "Failed to navigate to $PYTHON_SERVICE_DIR. Exiting."; exit 1; }

# # Install Python dependencies
# echo "Installing Python dependencies..."
# if [ -f "requirements.txt" ]; then
#     echo "Installing Python dependencies 
