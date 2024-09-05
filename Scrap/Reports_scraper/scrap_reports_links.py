import json
import csv
import re
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
def get_existing_groups(intrusion_sets='ATT&AK/intrusion_sets.json'):
    # Load the JSON data
    with open(intrusion_sets, 'r') as json_file:
        data = json.load(json_file)

    # Extract the required attributes
    extracted_data = []
    for item in data:
        intrusion_set_name = item.get('Intrusion Set Name')
        external_id = item.get('External ID')
        if intrusion_set_name and external_id:
            extracted_data.append({'group_id': external_id, 'group_name': intrusion_set_name, 'links': ''})
    return extracted_data

# Function to transform a name
def transform_name(name):
    return name.replace(' ', '+')

def fetch_page_content_with_selenium(url):
    chrome_options = webdriver.ChromeOptions()
    chrome = webdriver.Chrome(options=chrome_options)
    time.sleep(5)
    chrome.get(url)
    page_source = chrome.page_source
    chrome.quit()  # Use quit() instead of close() to ensure the driver is properly closed
    return page_source

# Function to get and filter links from Google News search
def get_filtered_links_from_google_news(transformed_name, sleep_time):
    url = f"https://www.google.fr/search?q=threat-attack+%22{transformed_name}%22+report&tbm=nws"
    print(f"Fetching URL: {url}")  # Debugging line
    chrome_options = webdriver.ChromeOptions()
    chrome = webdriver.Chrome(options=chrome_options)
    time.sleep(3)
    chrome.get(url)
    time.sleep(sleep_time)
    page_content = chrome.page_source
    
    
    # Define a regex pattern to find links that start with "https://www." and end with "&"
    pattern = r'https://www\.(?!google)[^\s"&]+&'

    # Find all links matching the pattern
    all_links = re.findall(pattern, page_content)
    
    # Remove trailing "&" from each link
    filtered_links = [link.rstrip('&') for link in all_links]
    
    print(f"Found {len(filtered_links)} filtered links")  # Debugging line

    return filtered_links

# Function to save data to CSV
def save_to_csv(data, file_path):
    with open(file_path, 'w', newline='') as csv_file:
        fieldnames = ['group_id', 'group_name', 'links']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Load existing CSV to find the starting index
def load_existing_csv(file_path):
    existing_data = []
    try:
        with open(file_path, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            existing_data = list(reader)
    except FileNotFoundError:
        # CSV file does not exist
        pass
    return existing_data
def scrap_reports_links(extracted_data,csv_file_path = 'reports_links.csv'):


    chrome_options = webdriver.ChromeOptions()
    chrome = webdriver.Chrome(options=chrome_options)
    # Load existing data and find the starting index
    existing_data = load_existing_csv(csv_file_path)
    existing_ids = set(row['group_id'] for row in existing_data)
    start_index = len(existing_data)

    # Process each row and get links
    sleep_time = 20
    for i, item in enumerate(extracted_data):
        if item['group_id'] in existing_ids:
            # Skip if already processed
            continue

        transformed_name = transform_name(item['group_name'])
        print(f"Processing name: {item['group_name']} (Transformed: {transformed_name})")  # Debugging line
        links = get_filtered_links_from_google_news(transformed_name, sleep_time)
        sleep_time = 5
        item['links'] = ', '.join(links)  # Join links with a comma
        
        # Save every 5 rows
        if (i + 1) % 5 == 0 or i + 1 == len(extracted_data):
            save_to_csv(existing_data + extracted_data[:i + 1], csv_file_path)
    chrome.quit()
    print(f"Data has been successfully saved to {csv_file_path}")
    
