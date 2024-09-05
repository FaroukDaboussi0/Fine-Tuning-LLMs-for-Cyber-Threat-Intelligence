import csv
import json
import os
import time

from Models.GeminiApi import bard


def clean_response(response):
        """
        Cleans the response by extracting valid JSON objects.
        
        Parameters:
        - response (str): The response from the bard function.
        
        Returns:
        - cleaned_objects (list): A list of cleaned JSON objects.
        """
        lines = response.split("\n")
        json_objects = []
        in_json_object = False
        json_buffer = []

        for line in lines:
            if line.startswith("{"):
                in_json_object = True
                json_buffer.append(line)
            elif line.startswith("}") and in_json_object:
                json_buffer.append(line)
                json_objects.append("\n".join(json_buffer))
                in_json_object = False
                json_buffer = []
            elif in_json_object:
                json_buffer.append(line)

        return json_objects


def generate_cves_qcm(cves):

    cve_qcms = {}
    

    # Initialize variables
    base_text = '''You are a cybersecurity expert specializing in Common Vulnerabilities and Exposures (CVE). Given the text below, please generate a maximum of 40 multiple-choice questions (MCQ) with four possible options.

Follow these requirements:

1. **Question Format**: The question must have four options. The options should be challenging and require careful consideration. Avoid creating options that could be interpreted as correct under different circumstances.
2. **Target Audience**: The question should be suitable for security professionals with three to five years of experience in software security. Avoid generic questions.
3. **Content Coverage**: Aim to cover various aspects of the provided text to assess the candidate's knowledge.
4. **Technical Accuracy**: Use precise terminology and concepts relevant to software security.
5. **CVE Integration**: Include the CVE ID and description in the question.
6. **Question Structure**: Ensure the question includes a clear premise and four distinct options.
7. **Output Format**: Return the output in JSON format with fields: CVE_ID, Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation.
8. **Be sensitive to separating between rows generated**.
9. **Do not use commas in the content**; use them only to separate between fields in the JSON format.

### Example Output
```json
{
  "CVE_ID": "CVE-2023-12345",
  "Question": "What is the primary impact of CVE-2023-12345?",
  "Option A": "Information disclosure",
  "Option B": "Denial of service",
  "Option C": "Code execution",
  "Option D": "Privilege escalation",
  "Correct Answer": "Option C",
  "Explanation": "CVE-2023-12345 allows an attacker to execute arbitrary code due to improper input validation."
}
### text : 

'''

    accumulated_text = base_text + "\n\n"
    max_cves_per_request = 40
    cve_counter = 1

    
    for index, cve in cves.itterows():
        # Convert the CVE object to a textual representation
        text_representation = (
            f"CVE ID: {cve['CVE_ID']}\n"
            f"Description: {cve['Description']}\n"
            f"CVSS Vector String: {cve['CVSS_Vector_String']}\n"
            f"CWE IDs: {cve['CWE_IDs']}\n"
        )

        
        # Accumulate the text
        accumulated_text += text_representation + "\n\n"
        cve_counter += 1
        
        # Every 10 CVEs, pass the accumulated text to the bard function
        if cve_counter % max_cves_per_request == 0:
            # Call the bard function with the accumulated text
            response = bard(accumulated_text)
            print("done")
            time.sleep(5)
            # Clean the response
            json_objects = clean_response(response)
            
            cve_qcms.append(json_objects)
            # Reset accumulated text
            accumulated_text = base_text + "\n\n"
    
    # Process any remaining CVEs not divisible by 10
    if accumulated_text.strip() and cve_counter % max_cves_per_request != 0:
        response = bard(accumulated_text)
        # Clean the response
        json_objects = clean_response(response)
        
        cve_qcms.append(json_objects)


    return cve_qcms