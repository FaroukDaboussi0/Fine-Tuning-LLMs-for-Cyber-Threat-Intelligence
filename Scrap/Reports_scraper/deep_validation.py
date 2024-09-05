import pandas as pd
import numpy as np

from Models.GeminiApi import bard
def build_prompt(df):
        reports = "\n".join([
            f"report {index} : {row['rapport']}"
            for index, row in df.iterrows()
        ])
        prompt = f'''I'm providing {len(df)} reports. For each report, if this cyber threat report contains detailed descriptions of techniques used or IOCs (IPs, domains, hashes, etc.) that can be analyzed to determine the group actor, generate an output of 1. Otherwise, generate 0.
        {reports}
        Output format: list of {len(df)} elements, each being 0 or 1, no extra words or punctuation.
        Example output: [0,1,0,1,1,0]
        '''
        return prompt


# Function to convert response string to list of integers
def convert_response_to_list(response):
    # Remove the brackets and split by comma
    response = response.strip()
    response_list = response.strip('[]').split(',')
    # Strip whitespace and convert each element to an integer
    return [int(item.strip()) for item in response_list]



def deep_validation(tta ,final_reports = "IOC_rapports.tsv"):

    df = pd.read_csv(tta, sep="\t")

    # Split the DataFrame into 10 sub-DataFrames
    sub_dfs = np.array_split(df, 10)

   
    # List to store the rows
    rows = []

    # Generate and process responses for each sub-DataFrame
    for i, sub_df in enumerate(sub_dfs):
        prompt = build_prompt(sub_df)
        resp = bard(prompt)  # Assuming bard is a function that takes a prompt and returns a response
        print(resp)
        try:
            resp_list = convert_response_to_list(resp)
        except ValueError as e:
            print(f"Error converting response to list for sub-DataFrame {i+1}: {e}")
            continue
        print(resp_list)
        # Iterate over the list and append rows based on the condition
        for index, value in enumerate(resp_list):
            if value == 1:
                rows.append(sub_df.iloc[index].to_dict())

    # Now `rows` contains the rows that met the condition
    df = pd.DataFrame(rows)
    df.to_csv(final_reports, sep="\t", index=False)
