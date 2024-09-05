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

def generate_techniques_qcm(techniques, output_json_filename='QCM_TECHNIQUES.json'):
    techniques_qcms = {}
    

    # Initialize variables
    base_text = '''You are a cybersecurity expert specializing in MITRE ATT&CK techniques. Given the text below, please generate a maximum of 10 multiple-choice questions (MCQ) with four possible options.

Follow these requirements:

1. **Question Format**: The question must have four options. The options should be challenging and require careful consideration. Avoid creating options that could be interpreted as correct under different circumstances.
2. **Target Audience**: The question should be suitable for security professionals with three to five years of experience in cybersecurity. Avoid generic questions.
3. **Content Coverage**: Aim to cover various aspects of the provided text to assess the candidate's knowledge.
4. **Technical Accuracy**: Use precise terminology and concepts relevant to cybersecurity.
5. **MITRE ATT&CK Integration**: Include the MITRE ATT&CK Technique ID and name in the question.
6. **Question Structure**: Ensure the question includes a clear premise and four distinct options.
7. **Output Format**: Return the output in JSON format with fields: Technique_ID, Question, Option A, Option B, Option C, Option D, Correct Answer, Explanation.
8. **Be sensitive to separating between rows generated**.
9. **Do not use commas in the content**; use them only to separate between fields in the JSON format.

### Example Output
```json
{
  "Technique_ID": "T1003",
  "Question": "What is a common technique used for Credential Dumping?",
  "Option A": "Phishing",
  "Option B": "Memory Dumping",
  "Option C": "SQL Injection",
  "Option D": "Cross-Site Scripting",
  "Correct Answer": "Option B",
  "Explanation": "Credential Dumping involves extracting credentials from system memory, which can be done using various tools and techniques designed to dump memory contents."
}
### text : 

'''

    accumulated_text = base_text + "\n\n"
    max_techniques_per_request = 5

    

    if isinstance(techniques, list):
        # Iterate over the techniques
        for index, technique in enumerate(techniques):
            # Convert the technique object to a textual representation
            text_representation = json.dumps(technique, indent=2)

            # Accumulate the text
            accumulated_text += text_representation + "\n\n"

            # Every 5 techniques, pass the accumulated text to the bard function
            if (index + 1) % max_techniques_per_request == 0:
                # Call the bard function with the accumulated text
                response = bard(accumulated_text)
                print("done")
                time.sleep(5)
                # Clean the response
                json_objects = clean_response(response)

                techniques_qcms.append(json_objects)

                # Reset accumulated text
                accumulated_text = base_text + "\n\n"
        
        # Process any remaining techniques not divisible by 10
        if accumulated_text.strip():
            response = bard(accumulated_text)
            # Clean the response
            json_objects = clean_response(response)

            techniques_qcms.append(json_objects)
    return techniques_qcms


