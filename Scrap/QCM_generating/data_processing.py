import csv
import random

def take_random_rows(input_csv, output_csv, num_rows):
    """
    Take a specified number of random rows from an input CSV file and save them to an output CSV file.

    Parameters:
    - input_csv (str): The path to the input CSV file.
    - output_csv (str): The path to the output CSV file.
    - num_rows (int): The number of random rows to select. Default is 200.

    Returns:
    - None
    """
    # Read the input CSV file
    with open(input_csv, 'r', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = list(reader)
    
    # Check if the number of rows is less than the required number
    if len(rows) <= num_rows:
        print(f"Input file has only {len(rows)} rows, which is less than or equal to the requested {num_rows} rows.")
        return
    
    # Separate header and data rows
    header, data = rows[0], rows[1:]
    
    # Take random rows
    selected_rows = random.sample(data, num_rows)
    
    # Write the selected rows to the output CSV file
    with open(output_csv, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(header)  # Write the header
        writer.writerows(selected_rows)  # Write the selected rows

import json
import csv

def sanitize_tsv_value(value):
    # Example sanitization function
    return value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ')

def qcm_json_to_tsv(json_file_path, tsv_filename):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    with open(tsv_filename, 'w', newline='', encoding='utf-8') as tsv_file:
        writer = csv.writer(tsv_file, delimiter='\t')
        # Write header row
        writer.writerow(['Reference', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Prompt', 'GT', 'Explanation'])
        
        for obj in data:
            reference = sanitize_tsv_value(obj.get('Reference', ''))
            question = sanitize_tsv_value(obj.get('Question', ''))
            option_a = sanitize_tsv_value(obj.get('Option A', ''))
            option_b = sanitize_tsv_value(obj.get('Option B', ''))
            option_c = sanitize_tsv_value(obj.get('Option C', ''))
            option_d = sanitize_tsv_value(obj.get('Option D', ''))
            correct_answer = sanitize_tsv_value(obj.get('Correct Answer', ''))
            explanation = sanitize_tsv_value(obj.get('Explanation', ''))

            # Normalize the correct answer
            correct_answer_lower = correct_answer.lower()
            if correct_answer_lower in [option_a.lower(), 'option a']:
                correct_answer = 'A'
            elif correct_answer_lower in [option_b.lower(), 'option b']:
                correct_answer = 'B'
            elif correct_answer_lower in [option_c.lower(), 'option c']:
                correct_answer = 'C'
            elif correct_answer_lower in [option_d.lower(), 'option d']:
                correct_answer = 'D'

            prompt = f"You are given a multiple-choice question (MCQ) from a Cyber Threat Intelligence (CTI) knowledge benchmark dataset. Your task is to choose the best option among the four provided. Return your answer as a single uppercase letter: A, B, C, or D.  **Question:** {question} ? **Options:** A) {option_a} B) {option_b} C) {option_c} D) {option_d} **Important:** The last line of your answer should contain only the single letter corresponding to the best option, with no additional text. "

            
            writer.writerow([reference, question, option_a, option_b, option_c, option_d, prompt, correct_answer, explanation])


def validate_tsv_format(tsv_filename):
    try:
        with open(tsv_filename, 'r', encoding='utf-8') as tsv_file:
            reader = csv.reader(tsv_file, delimiter='\t')
            
            # Read header
            header = next(reader)
            expected_columns = ['Reference', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Prompt', 'GT', 'Explanation']
            
            if header != expected_columns:
                print(f"Header mismatch: Expected {expected_columns}, found {header}")
                return False

            # Check each row
            for i, row in enumerate(reader, start=2):  # Start at row 2 to account for header
                if len(row) != len(expected_columns):
                    print(f"Row {i} column count mismatch: Expected {len(expected_columns)}, found {len(row)}")
                    return False
                
                # Example check: Ensure each field is a string (you can add more type checks as needed)
                for value in row:
                    if not isinstance(value, str):
                        print(f"Row {i} value type mismatch: Expected string, found {type(value).__name__}")
                        return False
            
        print("TSV format is valid.")
        return True
    
    except Exception as e:
        print(f"Error reading TSV file: {e}")
        return False



def remove_rows_with_missing_values(input_tsv_filename, output_tsv_filename):
    header = None
    rows_to_keep = []
    
    try:
        # Read the TSV file
        with open(input_tsv_filename, 'r', encoding='utf-8') as infile:
            reader = csv.reader(infile, delimiter='\t')
            
            # Read header
            header = next(reader)
            expected_columns = ['Reference', 'Question', 'Option A', 'Option B', 'Option C', 'Option D', 'Prompt', 'GT', 'Explanation']
            
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

# Example usage

