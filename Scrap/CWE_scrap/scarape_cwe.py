import re
import csv

    
import csv
import requests
from bs4 import BeautifulSoup

def get_cwe_ids(data):
    with open(data, 'r', encoding='utf-8') as file:
        xml_text = file.read()

    # Define a regular expression pattern to find ID and Name attributes in <Weakness> tags
    pattern = r'<Weakness\s+ID="(\d+)"\s+Name="([^"]+)".*?>'

    # Find all occurrences of the pattern in the XML text
    matches = re.findall(pattern, xml_text, re.DOTALL)
    ids = []
    for ID, Name in matches:
        id_value = ID  
        ids.append(id_value)
    return ids

def scrape_cwe_data(cwe_id, output_file="cwe_data.csv"):
    """
    Scrapes CWE data from the given CWE ID and writes it to a CSV file.

    Args:
        cwe_id (str): The CWE ID to scrape data for.
        output_file (str, optional): The filename to use for the CSV output. Defaults to "cwe_data.csv".

    Raises:
        requests.exceptions.RequestException: If an error occurs during the HTTP request.
    """
    url = f"https://cwe.mitre.org/data/definitions/{cwe_id}.html"
    headers = {
        "User-Agent": "MyPythonScraper via requests lib (contact: faroukdaboussi2009@gmail.com)"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.RequestException as e:
        print(f"Error fetching CWE data for {cwe_id}: {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    print(f"{cwe_id} is done")
    
    # Extracting Description
    description_div = soup.find("div", id=f"oc_{cwe_id}_Description")
    description = description_div.text.strip() if description_div else ""

    # Extracting Extended Description
    extended_description_div = soup.find("div", id=f"oc_{cwe_id}_Extended_Description")
    extended_description = extended_description_div.text.strip() if extended_description_div else ""

    # Extracting References
    references_div = soup.find("div", id=f"oc_{cwe_id}_References")
    references = [a.get("href") for a in references_div.find_all("a") if a.get("href")] if references_div else []

    data = {
        "ID": cwe_id,
        "Description": description,
        "Extended Description": extended_description,
        "References": references
    }

    return data

def scrap_cwe():
    """
    Main function to read CWE IDs from a CSV file, scrape data, and save it to a new CSV file.
    """
    output_file = 'cwe_data.csv'  # Output CSV filename
    id_list_filename = 'output.csv'  # Input CSV filename containing CWE IDs

    list_of_cwe_ids = get_cwe_ids(id_list_filename)
    scraped_data = []

    for cwe_id in list_of_cwe_ids:
        data = scrape_cwe_data(cwe_id)
        if data:
            scraped_data.append(data)

    # Save data to CSV after iterating through all IDs
    with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=scraped_data[0].keys())
        writer.writeheader()
        writer.writerows(scraped_data)

