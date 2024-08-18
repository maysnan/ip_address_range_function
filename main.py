import os
import json
import csv
from datetime import datetime, timezone
from google.cloud import storage
from urllib.request import urlopen
from urllib.error import HTTPError
import google.api_core.exceptions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the URLs for the JSON files
IPRANGE_URL = "https://www.gstatic.com/ipranges/goog.json"

# Define the Google Cloud Storage bucket name and folder structure
BUCKET_NAME = "ip-address-range"
GOOGLE_CLOUD_PROJECT = "gsuite-logger-432519"
IPV4_FOLDER = "google_ip_address_ranges/logs/ipv4s/"
IPV6_FOLDER = "google_ip_address_ranges/logs/ipv6s/"
URLS_FOLDER = "google_ip_address_ranges/urls/"

# Utility function for error handling
def handle_error(message):
    logging.error(message)

# Function to read the URL and return JSON data
def read_url(url):
    try:
        return json.loads(urlopen(url).read())
    except (IOError, HTTPError) as e:
        handle_error(f"CSV Upload Failed: Invalid HTTP response from {url}: {str(e)}")
    except json.decoder.JSONDecodeError as e:
        handle_error(f"CSV Upload Failed: Could not parse HTTP response from {url}: {str(e)}")

# Function to write a list of IP addresses to a CSV file in the /tmp directory
def write_csv(filename, ip_list):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for ip in ip_list:
            writer.writerow([ip])

# Function to extract IPv4 and IPv6 addresses and write them to CSV files in the /tmp directory
def extract_and_write_csv(data):
    ipv4_list = [e.get("ipv4Prefix") for e in data["prefixes"] if "ipv4Prefix" in e]
    ipv6_list = [e.get("ipv6Prefix") for e in data["prefixes"] if "ipv6Prefix" in e]
    
    # Date suffix for filenames
    date_suffix = datetime.now(timezone.utc).strftime('%Y%m%d')
    
    # Write to /tmp directory
    ipv4_filename = f"/tmp/ipv4_{date_suffix}.csv"
    ipv6_filename = f"/tmp/ipv6_{date_suffix}.csv"
    
    write_csv(ipv4_filename, ipv4_list)
    write_csv(ipv6_filename, ipv6_list)

    # File paths for URLs
    ipv4_url_filename = f"{URLS_FOLDER}ip4.csv"
    ipv6_url_filename = f"{URLS_FOLDER}ip6.csv"

    return ipv4_filename, ipv6_filename, ipv4_url_filename, ipv6_url_filename

# Function to upload files to Google Cloud Storage and make them public
def upload_to_gcloud_and_make_public(local_filename, cloud_filename):
    try:
        client = storage.Client()  # Using default credentials
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(cloud_filename)
        logging.info(f"Uploading {local_filename} to bucket {BUCKET_NAME}/{cloud_filename}...")
        blob.upload_from_filename(local_filename)
        blob.make_public()  # Make the file public
        logging.info(f"Uploaded and made public {local_filename} at {blob.public_url}")
    except google.api_core.exceptions.NotFound as e:
        handle_error(f"CSV Upload Failed: Bucket not found: {str(e)}")
    except Exception as e:
        handle_error(f"CSV Upload Failed: An error occurred during upload: {str(e)}")

# Main process
def process_ip_ranges():
    data = read_url(IPRANGE_URL)
    if data:
        logging.info(f"Data published: {data.get('creationTime')}")
        ipv4_filename, ipv6_filename, ipv4_url_filename, ipv6_url_filename = extract_and_write_csv(data)
        
        # Upload the latest IP files to the URLs folder and make them public
        upload_to_gcloud_and_make_public(ipv4_filename, ipv4_url_filename)
        upload_to_gcloud_and_make_public(ipv6_filename, ipv6_url_filename)

        # Upload copies of the IP files to the logs folders with date suffixes
        upload_to_gcloud_and_make_public(ipv4_filename, f"{IPV4_FOLDER}{os.path.basename(ipv4_filename)}")
        upload_to_gcloud_and_make_public(ipv6_filename, f"{IPV6_FOLDER}{os.path.basename(ipv6_filename)}")
        
        logging.info("CSV files created, uploaded to GCloud bucket, and made public.")
    else:
        handle_error("CSV Upload Failed: Could not retrieve data from the IP range source. Please check the Google Cloud IP Addresses Range Service.")

# Cloud Function entry point
def ipAddressRangeFunction(request):
    process_ip_ranges()
    return "IP Address ranges processed and uploaded successfully."
