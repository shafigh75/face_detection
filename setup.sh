#!/bin/bash

# Check if Docker is installed
if ! [ -x "$(command -v docker)" ]; then
  echo 'Docker is not installed. Installing Docker...'
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
fi

# Check if Docker Compose is installed
if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Docker Compose is not installed. Installing Docker Compose...'
  curl -L "https://github.com/docker/compose/releases/download/1.29.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  chmod +x /usr/local/bin/docker-compose
fi

# Print the version of Docker and Docker Compose
echo 'Docker version:'
docker --version
echo 'Docker Compose version:'
docker-compose --version

# start redis as docker image
docker-compose up -d

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