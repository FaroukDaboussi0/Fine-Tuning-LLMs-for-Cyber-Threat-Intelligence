import csv
import json
import os
import time

from Models.GeminiApi import bard



def generate_capec_qcm(capecs):
   
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
    capecs_qcms = {}
    # Initialize variables
    base_text = '''You are a cybersecurity expert specializing in Common Attack Pattern Enumeration and Classification (CAPEC). Given the text below, please generate a maximum of 20 multiple-choice questions (MCQ)  with four possible options ( 1 question for each CAPEC provided in the text below).

Follow these requirements:

1. **Question Format**: The question must have four options. The options should be challenging and require careful consideration. Avoid creating options that could be interpreted as correct under different circumstances.
2. **Target Audience**: The question should be suitable for security professionals with three to five years of experience in software security. Avoid generic questions.
3. **Content Coverage**: Aim to cover various aspects of the provided text to assess the candidate's knowledge.
4. **Technical Accuracy**: Use precise terminology and concepts relevant to software security.
5. **CAPEC Integration**: Include the CAPEC ID and name in the question.
6. **Question Structure**: Ensure the question includes a clear premise and four distinct options.
7. **Output Format**: Return the output in JSON format with fields: CAPEC_ID, Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation.
8. **Be sensitive to separating between rows generated**.
9. **Do not use commas in the content**; use them only to separate between fields in the JSON format.

### Example Output
```json
{
  "CAPEC_ID": "CAPEC-1",
  "Question": "What is the primary goal of a brute force attack?",
  "Option A": "To exploit a vulnerability in the application",
  "Option B": "To guess passwords by trying all possible combinations",
  "Option C": "To perform a man-in-the-middle attack",
  "Option D": "To inject malicious SQL queries",
  "Correct Answer": "Option B",
  "Explanation": "A brute force attack involves trying all possible password combinations to gain unauthorized access."
}
### text : 

'''

    accumulated_text = base_text + "\n\n"
    max_capecs_per_request = 20
    capec_counter = 1

    for index, capec in capecs.itterows():
        # Convert the CAPEC object to a textual representation
        text_representation = (f"CAPEC ID: {capec['ID']}\n"
                                            f"Name: {capec['Name']}\n"
                                            f"Abstraction: {capec['Abstraction']}\n"
                                            f"Status: {capec['Status']}\n"
                                            f"Description: {capec['Description']}\n"
                                            f"Alternate Terms: {capec['Alternate Terms']}\n"
                                            f"Likelihood Of Attack: {capec['Likelihood Of Attack']}\n"
                                            f"Typical Severity: {capec['Typical Severity']}\n"
                                            f"Related Attack Patterns: {capec['Related Attack Patterns']}\n"
                                            f"Execution Flow: {capec['Execution Flow']}\n"
                                            f"Prerequisites: {capec['Prerequisites']}\n"
                                            f"Skills Required: {capec['Skills Required']}\n"
                                            f"Resources Required: {capec['Resources Required']}\n"
                                            f"Indicators: {capec['Indicators']}\n"
                                            f"Consequences: {capec['Consequences']}\n"
                                            f"Mitigations: {capec['Mitigations']}\n"
                                            f"Related Weaknesses: {capec['Related Weaknesses']}\n")
                        
        # Accumulate the text
        accumulated_text += text_representation + "\n\n"
        capec_counter += 1
        
        # Every 10 CAPECs, pass the accumulated text to the bard function
        if capec_counter % max_capecs_per_request == 0:
            # Call the bard function with the accumulated text
            response = bard(accumulated_text)
            print("done")
            time.sleep(5)
            # Clean the response
            json_objects = clean_response(response)
            capecs_qcms.append(json_objects)
            
            
            # Reset accumulated text
            accumulated_text = base_text + "\n\n"
    
    # Process any remaining CAPECs not divisible by 10
    if accumulated_text.strip() and capec_counter % max_capecs_per_request != 0:
        response = bard(accumulated_text)
        # Clean the response
        json_objects = clean_response(response)
        
        capecs_qcms.append(json_objects)
    return capecs_qcms