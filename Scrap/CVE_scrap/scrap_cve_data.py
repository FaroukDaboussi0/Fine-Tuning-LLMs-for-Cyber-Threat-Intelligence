import requests
from bs4 import BeautifulSoup
import csv
import os
import time
from requests.exceptions import RequestException
from urllib3.exceptions import ProtocolError, IncompleteRead

def extract_cve_ids_from_csv(filename):
    """
    Extracts CVE IDs from a CSV file.

    Args:
        filename (str): Path to the CSV file containing CVE IDs.

    Returns:
        list: A list of CVE IDs.
    """
    cve_ids = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            cve_ids.append(row[0])
    return cve_ids

def scrape_cve_data(cve_id):
    """
    Scrapes detailed data for a given CVE ID from the NVD website.

    Args:
        cve_id (str): The CVE ID to scrape data for.

    Returns:
        dict: A dictionary containing CVE details such as description, date published, CVSS vector string, CWE IDs, and hyperlinks.
    """
    url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
    headers = {
        "User-Agent": "MyPythonScraper via requests lib (contact: faroukdaboussi2009@gmail.com)"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except (RequestException, ProtocolError, IncompleteRead) as e:
        print(f"Error fetching {cve_id}: {e}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract description
    description_tag = soup.find('p', {'data-testid': 'vuln-description'})
    if description_tag:
        description = description_tag.get_text(separator="\n", strip=True)
        description = ' '.join(description.split())  # Replace newlines with spaces and normalize whitespace
    else:
        description = None

    # Extract date published
    date_published_tag = soup.find('span', {'data-testid': 'vuln-published-on'})
    date_published = date_published_tag.get_text(strip=True) if date_published_tag else None

    # Extract CVSS vector string
    vector_string_tag = soup.find('span', {'data-testid': 'vuln-cvss3-nist-vector'})
    if not vector_string_tag:
        vector_string_tag = soup.find('span', {'data-testid': 'vuln-cvss2-panel-vector'})
    vector_string = vector_string_tag.get_text(strip=True) if vector_string_tag else None

    # Extract CWE IDs
    cwe_table = soup.find('table', {'data-testid': 'vuln-CWEs-table'})
    cwe_ids = []
    if cwe_table:
        rows = cwe_table.find_all('tr', {'data-testid': lambda x: x and x.startswith('vuln-CWEs-row')})
        for row in rows:
            cwe_id_tag = row.find('td', {'data-testid': lambda x: x and x.startswith('vuln-CWEs-link')})
            cwe_id = cwe_id_tag.get_text(strip=True) if cwe_id_tag else None
            if cwe_id:
                cwe_ids.append(cwe_id)

    # Extract Hyperlinks
    hyperlink_table = soup.find('table', {'data-testid': 'vuln-hyperlinks-table'})
    hyperlinks = []
    if hyperlink_table:
        rows = hyperlink_table.find_all('tr', {'data-testid': lambda x: x and x.startswith('vuln-hyperlinks-row')})
        for row in rows:
            hyperlink_tag = row.find('a')
            hyperlink = hyperlink_tag['href'] if hyperlink_tag else None
            if hyperlink:
                hyperlinks.append(hyperlink)
    
    return {
        'CVE_ID': cve_id,
        'Description': description,
        'Date_Published': date_published,
        'CVSS_Vector_String': vector_string,
        'CWE_IDs': ', '.join(cwe_ids) if cwe_ids else None,
        'Hyperlinks': ', '.join(hyperlinks) if hyperlinks else None
    }

def save_to_csv(data, filename, mode='a'):
    """
    Saves data to a CSV file.

    Args:
        data (list): List of dictionaries containing data to save.
        filename (str): Path to the CSV file.
        mode (str): File open mode ('a' for append). Defaults to 'a'.
    """
    keys = data[0].keys()
    with open(filename, mode, newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        if output_file.tell() == 0:  # Write header if file is empty
            dict_writer.writeheader()
        dict_writer.writerows(data)

def count_csv_rows(file_path):
    """
    Counts the number of rows in a CSV file excluding the header.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        int: The number of rows in the CSV file.
    """
    if not os.path.exists(file_path):
        return 0
    
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        row_count = sum(1 for row in reader)
        return row_count - 1  # Subtract the header row

def scrap_cve_data_from_links(input_csv_filename, output_filename="cve_detailed_data.csv", batch_size=100):
    """
    Main function to process CVE IDs, scrape detailed data, and save to CSV.

    Args:
        input_csv_filename (str): Path to the input CSV file containing CVE IDs.
        output_filename (str): Path to the output CSV file. Defaults to 'cve_detailed_data.csv'.
        batch_size (int): Number of records to save in each batch. Defaults to 100.
    """
    cve_ids = extract_cve_ids_from_csv(input_csv_filename)
    existing_rows = count_csv_rows(output_filename)
    start_index = existing_rows if existing_rows > 0 else 0
    cve_ids_to_process = cve_ids[start_index:]
    
    print(f"Starting at index: {start_index + 1}")

    all_data = []
    total_cves = len(cve_ids_to_process)
    start_time = time.time()

    for index, cve_id in enumerate(cve_ids_to_process, start=start_index + 1):
        data = scrape_cve_data(cve_id)
        if data:
            all_data.append(data)

        # Save data in batches
        if len(all_data) >= batch_size or index == total_cves + start_index:
            save_to_csv(all_data, output_filename)
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time * (total_cves / (index - start_index))
            estimated_remaining_time = estimated_total_time - elapsed_time
            print(f"Saved {index} CVEs to {output_filename}. Estimated remaining time: {estimated_remaining_time:.2f} seconds")
            all_data = []

