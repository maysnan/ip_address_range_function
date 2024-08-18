#!/bin/bash

# Define the folder paths
IPV4_FOLDER="./google_ip_address_ranges/logs/ipv4s"
IPV6_FOLDER="./google_ip_address_ranges/logs/ipv6s"
URLS_FOLDER="./google_ip_address_ranges/urls"

# Create the folders if they don't exist
mkdir -p "$IPV4_FOLDER"
mkdir -p "$IPV6_FOLDER"
mkdir -p "$URLS_FOLDER"

echo "Folder structure created or already exists."

