import pandas as pd

def preprocess_cti_data_to_llm(cti_rcm_path, cti_vsp_path, cti_mcq_path, cti_tta_path):
   

    # Read the CSV files
    cti_rcm = pd.read_csv(cti_rcm_path)  # columns: Description, GT
    cti_vsp = pd.read_csv(cti_vsp_path)  # columns: Description, GT
    cti_mcq = pd.read_csv(cti_mcq_path)  # columns: URL, Question, Option A, Option B, Option C, Option D, GT
    cti_tta = pd.read_csv(cti_tta_path)  # columns: URL, Text, GT

    # Define prompt templates
    cti_tta_prompt_template = ("You are given a threat report that describes a cyber incident. Any direct mentions of "
                               "the threat actor group, specific campaign names, or malware names responsible have been "
                               "replaced with [PLACEHOLDER]. Your task is to analyze the report and attribute the incident "
                               "to a known threat actor based on the techniques, tactics, procedures (TTPs), and any other "
                               "relevant information described. Please provide the name of the threat actor you believe is "
                               "responsible and briefly explain your reasoning. Threat Report: {Text}")
    
    cti_vsp_prompt_template = ("Analyze the following CVE description and calculate the CVSS v3.1 Base Score. Determine the "
                               "values for each base metric: AV, AC, PR, UI, S, C, I, and A. Summarize each metric's value and "
                               "provide the final CVSS v3.1 vector string. Ensure the final line of your response contains only "
                               "the CVSS v3 Vector String in the following format: Example format: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/"
                               "S:U/C:H/I:H/A:H CVE Description: {Description}")
    
    cti_rcm_prompt_template = ("Analyze the following CVE description and map it to the appropriate CWE. Provide a brief "
                               "justification for your choice. Ensure the last line of your response contains only the CWE ID. "
                               "CVE Description: {Description}")
    
    cti_mcq_prompt_template = ("You are given a multiple-choice question (MCQ) from a Cyber Threat Intelligence (CTI) knowledge "
                               "benchmark dataset. Your task is to choose the best option among the four provided. Return your "
                               "answer as a single uppercase letter: A, B, C, or D. **Question:** {question} ? **Options:** "
                               "A) {option_a} B) {option_b} C) {option_c} D) {option_d} **Important:** The last line of your "
                               "answer should contain only the single letter corresponding to the best option, with no additional text.")
    
    # Apply the prompts to each dataframe
    cti_tta['Prompt'] = cti_tta['Text'].apply(lambda text: cti_tta_prompt_template.format(Text=text))
    cti_vsp['Prompt'] = cti_vsp['Description'].apply(lambda desc: cti_vsp_prompt_template.format(Description=desc))
    cti_rcm['Prompt'] = cti_rcm['Description'].apply(lambda desc: cti_rcm_prompt_template.format(Description=desc))
    cti_mcq['Prompt'] = cti_mcq.apply(lambda row: cti_mcq_prompt_template.format(
        question=row['Question'],
        option_a=row['Option A'],
        option_b=row['Option B'],
        option_c=row['Option C'],
        option_d=row['Option D']
    ), axis=1)

    # Combine the prompt and GT columns into a new DataFrame for training
    cti_vsp_final = cti_vsp[['Prompt', 'GT']]
    cti_rcm_final = cti_rcm[['Prompt', 'GT']]
    cti_mcq_final = cti_mcq[['Prompt', 'GT']]
    cti_tta_final = cti_tta[['Prompt', 'GT']]

    # Concatenate all the dataframes into the final training DataFrame
    training_df = pd.concat([cti_vsp_final, cti_rcm_final, cti_mcq_final, cti_tta_final], ignore_index=True)

    return training_df
