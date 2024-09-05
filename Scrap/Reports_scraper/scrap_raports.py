import os
import pandas as pd
import json
import time
import re

from Models.GeminiApi import bard



def buil_prompt(group_name,rapport) :
    prompt = f"""
    Remove the noise from this cyber threat attack report, mask groupe name = {group_name}  in the rapport field with [PLACEHOLDER]. This will allow students to analyze the report and attribute the incident to a known threat actor based on the techniques, tactics, procedures (TTPs), and any other relevant information described.

    Important:
    - Noise includes links, contact us sections, other article suggestions, or any information that does not relate to the report.

    Output format: only the report no extra sentences 
    
    Text:
    {rapport}
    """
    return prompt
def escape_json_string(s):
    # Replace problematic characters with their escaped equivalents
    s = s.replace('"', '\\"')  # Escape double quotes
    s = s.replace('\\', '\\\\')  # Escape backslashes
    s = s.replace('\b', '\\b')  # Escape backspace
    s = s.replace('\f', '\\f')  # Escape form feed
    s = s.replace('\n', '\\n')  # Escape newline
    s = s.replace('\r', '\\r')  # Escape carriage return
    s = s.replace('\t', '\\t')  # Escape tab
    
    # For non-printable or control characters in Unicode, escape using \uXXXX
    # Convert any non-ASCII characters to their Unicode escape sequence
    return ''.join(f'\\u{ord(c):04x}' if ord(c) > 127 else c for c in s)


# Read the CSV file into a DataFrame
json_filename = "rapport.json"
json_filename = "rapport.json"
dirty_rapport = "reports_links_LMM.csv"
def clean_reports(dirty_rapport,json_filename):
    if os.path.exists(json_filename):
        with open(json_filename, 'rb') as file:
            json_bytes = file.read()
            json_string = json_bytes.decode('utf-8', errors='replace')
        start_index = json_string.count('"group_name":')+1
    else : 
        start_index = 0
    start_index = start_index 
    print(start_index)

    df = pd.read_csv(dirty_rapport, usecols=['URL', 'group_name', 'file_name']).reset_index(drop=True)
    df = df[start_index:]

    # Process each row in the DataFrame
    for idx, row in df.iterrows():
        group_name = row['group_name']
        file_name = row['file_name']
        url = row['URL']
        # Read the content of the file
        with open(f"rapport\{file_name}.txt", 'r', encoding='utf-8') as file:
            report_text = file.read()
        # Escape backslashes in the report text
        '''# Create a JSON object
        json_obj = {
            "group_name": group_name,
            "rapport": report_text
        }
        
        json_string = json.dumps(json_obj, ensure_ascii=False)
        final_prompt = prompt + json_string'''
        final_prompt = buil_prompt(str(group_name),str(report_text))
        response = bard(final_prompt)
        alias = bard(f"give me alias (also known as) of this cyber attackers group :{group_name} . output format : split alias with coma (,) no extra sentences . exemple : lets say goup name : MuddyWater  .output exempla  : APT34, Crambus, Helix Kitten, OilRig ").split(",")
        if response:
            # Escape backslashes in the report text
            response = escape_json_string(response)
            obj =   {
                "link" : url,
                "group_name" : group_name,
                "alias" : alias ,
                "rapport" : response

            }
            with open(json_filename, 'a', encoding='utf-8') as json_file:
                json.dump(obj, json_file, ensure_ascii=False)
                json_file.write("\n")
            print("rapport added!")



