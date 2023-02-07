#!/bin/bash

# Check if pip3 is installed
if command -v pip3 &> /dev/null; then
    echo "pip3 is already installed."
else
    echo "pip3 is not installed."
    # Install pip3
    sudo apt-get update
    sudo apt-get install -y python3-pip
    echo "pip3 has been installed."
fi

# install dependencies
pip3 install -r requirement.txt
make start