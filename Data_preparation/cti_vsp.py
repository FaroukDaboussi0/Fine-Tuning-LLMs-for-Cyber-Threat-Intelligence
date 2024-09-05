import pandas as pd


def preper_cti_vsp_to_train(input_csv,output_csv2):
    df = pd.read_csv(input_csv)

    # Create a new DataFrame with the desired columns and format
    output_df2 = pd.DataFrame()
    output_df2['CVE'] = df['CVE_ID']
    output_df2['Description'] = df['Description']
    # output_df2['Prompt'] = df['Description'].apply(lambda x: f"Analyze the following CVE description and calculate the CVSS v3.1 Base Score. Determine the values for each base metric: AV, AC, PR, UI, S, C, I, and A. Summarize each metric's value and provide the final CVSS v3.1 vector string. Valid options for each metric are as follows: - **Attack Vector (AV)**: Network (N), Adjacent (A), Local (L), Physical (P) - **Attack Complexity (AC)**: Low (L), High (H) - **Privileges Required (PR)**: None (N), Low (L), High (H) - **User Interaction (UI)**: None (N), Required (R) - **Scope (S)**: Unchanged (U), Changed (C) - **Confidentiality (C)**: None (N), Low (L), High (H) - **Integrity (I)**: None (N), Low (L), High (H) - **Availability (A)**: None (N), Low (L), High (H) Summarize each metric's value and provide the final CVSS v3.1 vector string. Ensure the final line of your response contains only the CVSS v3 Vector String in the following format: Example format: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H CVE Description: {x}")
    output_df2['GT'] = df['CVSS_Vector_String']

    output_df2 = output_df2.dropna()

    # Save the new DataFrame to a CSV file
    # Replace with your desired output CSV file name
    output_df2.to_csv(output_csv2, index=False)

    print(f"CSV file '{output_csv2}' created successfully.")
