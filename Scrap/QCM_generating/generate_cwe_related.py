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

def generate_cwes_qcm(cwes):
    cwes_qcm = {}
    

    # Initialize variables
    base_text = '''You are a cybersecurity expert specializing in Common Weakness Enumeration (CWE). Given the text below, please generate a maximum of 20 multiple-choice questions (MCQ) ( 1 question for each CWE provided in the text below) with four possible options.

Follow these requirements:

1. **Question Format**: The question must have four options. The options should be challenging and require careful consideration. Avoid creating options that could be interpreted as correct under different circumstances.
2. **Target Audience**: The question should be suitable for security professionals with three to five years of experience in software security. Avoid generic questions.
3. **Content Coverage**: Aim to cover various aspects of the provided text to assess the candidate's knowledge.
4. **Technical Accuracy**: Use precise terminology and concepts relevant to software security.
5. **CWE Integration**: Include the CWE ID and name in the question.
6. **Question Structure**: Ensure the question includes a clear premise and four distinct options.
7. **Output Format**: Return the output in JSON format with fields: CWE_ID, Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation.
8. **Be sensitive to separating between rows generated**.
9. **Do not use commas in the content**; use them only to separate between fields in the JSON format.

### Example Output
```json
{
  "CWE_ID": "CWE-79",
  "Question": "What is the primary cause of Cross-Site Scripting (XSS) vulnerabilities?",
  "Option A": "Incorrect input validation",
  "Option B": "Improper output encoding",
  "Option C": "Lack of authentication",
  "Option D": "Insecure storage",
  "Correct Answer": "Option B",
  "Explanation": "XSS vulnerabilities occur when an application includes untrusted data in a new web page without proper validation or escaping."
}
### text : 

'''

    accumulated_text = base_text + "\n\n"
    max_cwes_per_request = 20
    cwe_counter=1


 

    for index, cwe in cwes.itterows():
        # Convert the CWE object to a textual representation
        text_representation = f"CWE ID: {cwe['ID']}\nDescription: {cwe['Description']} . {cwe['Extended Description']} \n"
        
        # Accumulate the text
        accumulated_text += text_representation + "\n\n"
        cwe_counter += 1
        
        # Every 10 CWEs, pass the accumulated text to the bard function
        if cwe_counter % max_cwes_per_request == 0:
            # Call the bard function with the accumulated text
            response = bard(accumulated_text)
            print("done")
            time.sleep(5)
            # Clean the response
            json_objects = clean_response(response)
            
            cwes_qcm.append(json_objects)
            
            # Reset accumulated text
            accumulated_text = base_text + "\n\n"
    
    # Process any remaining CWEs not divisible by 10
    if accumulated_text.strip() and cwe_counter % max_cwes_per_request != 0:
        response = bard(accumulated_text)
        # Clean the response
        json_objects = clean_response(response)
        
        cwes_qcm.append(json_objects)
    
    return cwes_qcm

