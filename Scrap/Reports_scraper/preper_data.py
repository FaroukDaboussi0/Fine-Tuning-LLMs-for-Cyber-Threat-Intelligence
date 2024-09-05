import json
import csv
import re

import pandas as pd

def get_first_second_name(df, group_name):
    # Filter the DataFrame based on the specified group_name
    filtered_df = df[df['group_name'] == group_name]
    
    # Return the first 'second_name' value if it exists, otherwise None
    if not filtered_df.empty:
        return filtered_df['second_name'].iloc[0]
    return None
def transform_rapport(rapport, group_name, second_name):
    # Replace occurrences of group_name and second_name with [PLACEHOLDER]
    trans_rapport = rapport.replace(group_name, '[PLACEHOLDER]')
    trans_rapport = trans_rapport.replace(second_name, '[PLACEHOLDER]')
    return trans_rapport
# Function to unescape JSON string
def unescape_json_string(s):
    s = s.replace('\\"', '"')  # Unescape double quotes
    s = s.replace('\\\\', '\\')  # Unescape backslashes
    s = s.replace('\\b', '\b')  # Unescape backspace
    s = s.replace('\\f', '\f')  # Unescape form feed
    s = s.replace('\\n', '\n')  # Unescape newline
    s = s.replace('\\r', '\r')  # Unescape carriage return
    s = s.replace('\\t', '\t')  # Unescape tab
    
    # Unescape Unicode sequences
    def replace_unicode(match):
        return chr(int(match.group(1), 16))
    s = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, s)
    
    return s

# Function to sanitize TSV value
def sanitize_tsv_value(value):
    if isinstance(value, str):
        # Replace tabs with spaces
        value = value.replace('\t', ' ')
        # Replace newlines with spaces
        value = value.replace('\n', ' ').replace('\r', ' ')
    return value






def is_valid_tsv(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file, delimiter='\t')
        rows = list(reader)
        
        # Check if the file is empty
        if not rows:
            print("TSV file is empty.")
            return False
        
        # Check for consistent column count
        column_count = len(rows[0])
        for row in rows:
            if len(row) != column_count:
                print(f"Inconsistent column count at row: {row}")
                return False
        
        # Example: Check if URLs are valid in the 'link' column (assuming the first column is 'link')
        for row in rows[1:]:  # Skip header row
            link = row[0]
            if not link.startswith(('http://', 'https://')):
                print(f"Invalid URL found: {link}")
                return False
        
        print("TSV file is valid.")
        return True
    

def remove_rows_with_missing_values(input_tsv_filename, output_tsv_filename):
    expected_columns = ['link', 'group_name', 'rapport', 'prompt']
    header = None
    rows_to_keep = []
    
    try:
        # Read the TSV file
        with open(input_tsv_filename, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t')
            
            # Read header
            header = next(reader)
            
            if header != expected_columns:
                print(f"Header mismatch: Expected {expected_columns}, found {header}")
                return
            
            # Check each row
            for row in reader:
                if len(row) != len(expected_columns):
                    print(f"Row column count mismatch: Expected {len(expected_columns)}, found {len(row)}")
                    continue
                
                # Check if any value is missing
                if not any(not value.strip() for value in row):
                    rows_to_keep.append(row)
        
        # Write the cleaned data to a new TSV file
        with open(output_tsv_filename, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile, delimiter='\t')
            writer.writerow(header)
            writer.writerows(rows_to_keep)
        
        print(f"Rows with missing values have been removed. Cleaned data saved to {output_tsv_filename}")
    
    except Exception as e:
        print(f"Error processing TSV file: {e}")


def preper_report_to_tsv(reports_json,cleaned_reports_tsv,reports_links_csv) :
    reports_links_csv = pd.read_csv(reports_links_csv)
    # Open and read the JSON file
    reports_tsv = 'temp_reports_tsv.tsv'
    with open(reports_json, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Prepare TSV file for writing
    with open(reports_tsv, 'w', newline='', encoding='utf-8') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        
        # Write header row
        writer.writerow(['link', 'group_name', 'rapport', 'prompt'])
        
        # Process each object in the JSON data
        for obj in data:
            link = obj['link']
            group_name = obj['group_name']
            rapport = obj['rapport']
            second_name = get_first_second_name(reports_links_csv ,group_name )
            rapport = transform_rapport(rapport, group_name, second_name)
            # Unescape and sanitize the rapport field
            unc_rapp = unescape_json_string(rapport)
            tsv_rapp = sanitize_tsv_value(unc_rapp)
            prompt_tsv =f"You are given a threat report that describes a cyber incident. Any direct mentions of the threat actor group, specific campaign names, or malware names responsible have been replaced with [PLACEHOLDER]. Your task is to analyze the report and attribute the incident to a known threat actor based on the techniques, tactics, procedures (TTPs), and any other relevant information described. Please provide the name of the threat actor you believe is responsible and briefly explain your reasoning.  Threat Report:" + tsv_rapp
            # Write the processed data to the TSV file
            writer.writerow([link, group_name, tsv_rapp, prompt_tsv])
    
    remove_rows_with_missing_values(reports_tsv, cleaned_reports_tsv)
    is_valid = is_valid_tsv(cleaned_reports_tsv)
    return is_valid