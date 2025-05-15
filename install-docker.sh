#!/bin/bash

# Update system
echo "Updating system..."
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
echo "Adding user '$USER' to the docker group..."
sudo usermod -aG docker $USER

# Install Docker Compose plugin
echo "Installing Docker Compose plugin..."
sudo apt-get install -y docker-compose-plugin

# Verify installation
echo
echo "Installation complete."
docker --version
docker compose version

echo
echo "ou must log out and back in (or reboot) for group changes to take effect."

