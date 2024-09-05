import pandas as pd


def preper_cti_mcq_to_train(qcm_data,cti_mcq):
    df = pd.read_csv(qcm_data)
    final_df = pd.DataFrame()
    final_df["URL"] = df["Reference"]
    final_df["Question"] = df["Question"]
    final_df["Option A"] = df["Option A"]
    final_df["Option B"] = df["Option B"]
    final_df["Option C"] = df["Option C"]
    final_df["Option D"] = df["Option D"]
    final_df["GT"] = df["Correct Answer"]
    final_df.to_csv(cti_mcq)
   
