import pandas as pd


def preper_cti_rcm_to_train(input_csv,output_csv):
    df = pd.read_csv(input_csv)

    # Create a new DataFrame with the desired columns and format
    output_df = pd.DataFrame()
    output_df['CVE'] = df['CVE_ID']
    output_df['Description'] = df['Description']
    # output_df['Prompt'] = df['Description'].apply(lambda x: f"Analyze the following CVE description and map it to the appropriate CWE. Provide a brief justification for your choice. Ensure the last line of your response contains only the CWE ID.  CVE Description: {x}")
    output_df['GT'] = df['CWE_IDs']

    output_df = output_df.dropna()
    # Save the new DataFrame to a CSV file

    output_df.to_csv(output_csv, index=False)

    print(f"CSV file '{output_csv}' created successfully.")