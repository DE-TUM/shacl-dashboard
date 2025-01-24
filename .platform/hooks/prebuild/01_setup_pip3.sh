#!/bin/bash

# echo "Ensuring pip3 is installed..."

# # Check if Python3 is installed
# if ! command -v python3 &> /dev/null; then
#   echo "Python3 is not installed. Installing now..."
#   sudo dnf install -y python3 || { echo "Failed to install Python3"; exit 1; }
# fi

# # Ensure pip3 is installed and upgraded
# if ! command -v pip3 &> /dev/null; then
#   echo "pip3 is not installed. Installing now..."
#   python3 -m ensurepip || { echo "Failed to install pip3 using ensurepip"; exit 1; }
# fi

# echo "Upgrading pip3..."
# python3 -m pip install --upgrade pip || { echo "Failed to upgrade pip3"; exit 1; }

# echo "pip3 installation completed successfully."
