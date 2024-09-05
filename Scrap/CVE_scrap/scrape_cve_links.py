import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import os

def get_cve_links(url):
    """
    Fetches the CVE links from a given page URL.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        list: A list of dictionaries containing CVE IDs and their URLs.
    """
    headers = {
        "User-Agent": "MyPythonScraper via requests lib (contact: faroukdaboussi2009@gmail.com)"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.content, 'html.parser')

    cve_links = []
    for a_tag in soup.find_all('a', attrs={'data-testid': lambda x: x and x.startswith('vuln-detail-link-')}):
        cve_id = a_tag.text.strip()
        cve_url = f"https://nvd.nist.gov{a_tag.get('href')}"
        cve_links.append({'CVE ID': cve_id, 'URL': cve_url})
    
    return cve_links

def count_csv_rows(file_path):
    """
    Counts the number of rows in the CSV file excluding the header.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        int: The number of rows in the CSV file.
    """
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        row_count = sum(1 for row in reader)
        return row_count - 1  # Subtract the header row

def scrape_all_cve_links(output_file='cve_links.csv'):
    """
    Scrapes CVE links from all paginated pages and writes them to a CSV file in batches of 1000 rows.

    Args:
        output_file (str, optional): The filename to use for the CSV output. Defaults to 'cve_links.csv'.
    """
    base_url = "https://nvd.nist.gov/vuln/search/results?isCpeNameSearch=false&cvss_version=3&results_type=overview&form_type=Advanced&search_type=all&startIndex="
    increment = 20
    max_index = 154920  # Replace this with the actual max index if known
    batch_size = 1000

    # Determine the starting point by counting existing rows in the CSV file
    existing_rows = count_csv_rows(output_file)
    start_index = (existing_rows + 1) if existing_rows > 0 else 1
    
    print(f"Starting at index: {start_index}")

    all_cve_links = []

    while start_index <= max_index:
        print(f"Fetching page starting at index: {start_index}")
        url = f"{base_url}{start_index}"
        page_cve_links = get_cve_links(url)
        all_cve_links.extend(page_cve_links)
        start_index += increment

        # Write in batches of 1000 rows
        if len(all_cve_links) >= batch_size:
            with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['CVE ID', 'URL'])
                if existing_rows == 0:
                    writer.writeheader()
                writer.writerows(all_cve_links[:batch_size])
                all_cve_links = all_cve_links[batch_size:]  # Keep the remaining part for the next batch
                existing_rows += batch_size
                print(f"Written {existing_rows} rows to {output_file}")

    df = pd.DataFrame(all_cve_links, columns=['CVE ID', 'URL'])

    return df

