import csv
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

from Scrap.Reports_scraper.preper_data import preper_report_to_tsv
from Scrap.Reports_scraper.scrap_raports import clean_reports



# Configurations
SLEEP_TIME = 15
RETRY_COUNT = 2
RETRY_DELAY = 1
MAX_WORD_COUNT = 8000
MIN_OCCURRENCES = 2

# Initialize Selenium WebDriver
chrome_options = webdriver.ChromeOptions()
chrome = webdriver.Chrome(options=chrome_options)

def count_words(text):
    """Count words in a text."""
    return len(re.findall(r'\w+', text))

def fetch_with_retries(url, retries=RETRY_COUNT, delay=RETRY_DELAY):
    """Fetch URL content with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response
            else:
                print(f"Request failed with status code: {response.status_code} (Attempt {attempt + 1}/{retries})")
        except requests.exceptions.RequestException as e:
            print(f"Request failed with exception: {e} (Attempt {attempt + 1}/{retries})")
        time.sleep(delay)
    print(f"Request failed after {retries} attempts")
    return None

def process_links(row, sleep_time, driver=chrome):
    """Process and validate links from a row."""
    valid_links = []
    links = row.get('links', '').split(', ')
    link_num = 1
    for link in links:
        if not link:
            continue
        
        print(f"Processing link: {link}")
        try:
            response = fetch_with_retries(link)
            if response is None:
                driver.get(link)
                time.sleep(sleep_time)
                sleep_time = 3
                page_content = driver.page_source
            else:   
                page_content = response.content
            
            soup = BeautifulSoup(page_content, 'html.parser')
            article = soup.find('article') or soup.find('main') or soup.find('body')

            if article:
                article_text = article.get_text()
                word_count = count_words(article_text)
                print(f"Article word count: {word_count}")

                if word_count < MAX_WORD_COUNT and (
                    article_text.lower().count(row.get('group_name', '').lower()) >= MIN_OCCURRENCES or 
                    article_text.lower().count(row.get('second_name', '').lower()) >= MIN_OCCURRENCES):
                    valid_links.append(link)
                    file_path =  f"rapport/{row.get('group_name', '')}R{link_num}.txt"
                    with open(file_path, 'a', encoding='utf-8') as file:
                        file.write(article_text + "\n\n")  # Add newline between articles
                    link_num +=1
                else:
                    print(f"Link is invalid based on criteria: {link}")
            else:
                print(f"No suitable HTML element found in the response: {link}")
        
        except Exception as e:
            print(f"An error occurred: {e}")

    return ', '.join(valid_links)

def load_existing_csv(file_path):
    """Load existing data from a CSV file."""
    try:
        with open(file_path, 'r', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            return list(reader)
    except FileNotFoundError:
        return []

def validate_reports(reports_links = 'reports_links.csv',valid_reports_links_csv = 'valid_reports_links.csv'):
    valid_reports_links = 'temp_valid_reports_links.csv'

    existing_data = load_existing_csv(valid_reports_links)
    start_index = len(existing_data)
    extracted_data = pd.read_csv(reports_links)
    rows_to_write = []

    for i, row in extracted_data.iterrows():
        if i >= start_index :
            print(row)
            row_dict = row.to_dict()
            row_dict['links'] = process_links(row_dict, SLEEP_TIME, chrome)
            row_dict.pop('second_name', None)  # Remove 'second_name' if present
            rows_to_write.append(row_dict)

            if (i + 1) % 5 == 0 or i == len(extracted_data) - 1:
                with open(valid_reports_links, 'a', newline='') as csv_file:
                    fieldnames = ['group_id', 'group_name', 'links']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    
                    if start_index == 0:  # Write header only once
                        writer.writeheader()
                        start_index += 1
                    if rows_to_write:
                        writer.writerows(rows_to_write)
                    rows_to_write = []

    chrome.quit()
    # Open the input file for reading
    with open(valid_reports_links, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # Open the output file for writing
        with open(valid_reports_links_csv, 'w', newline='', encoding='utf-8') as outfile:
            fieldnames = ['URL', 'group_name', 'file_name']
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            # Write the header
            writer.writeheader()
            
            # Process each row in the input file
            for row in reader:
                group_name = row['group_name']
                links = row['links'].split(',')
                i=1
                for link in links:
                    writer.writerow({'URL': link, 'group_name': group_name, 'file_name': f"{group_name}R{i}"})
                    i+=1

    print("Processing complete. Check the output file for results.")
    print(f"Filtered data has been successfully saved to {valid_reports_links}")

def scrap_reports(reports_links_csv,reports_data_tsv):
    valid_reports_links_csv = r'Data\logs\valid_reports_links.csv'
    validate_reports(reports_links_csv,valid_reports_links_csv)
    cleaned_report_json="Data\logs\rapport.json"
    clean_reports(valid_reports_links_csv,json_filename=cleaned_report_json)
    reports_data_tsv = 'Data\logs\taa.tsv'
    preper_report_to_tsv(cleaned_report_json,reports_data_tsv,reports_links_csv) 
