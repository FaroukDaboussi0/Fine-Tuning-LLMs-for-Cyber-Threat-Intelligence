import pandas as pd


def preper_cti_tta_to_train(reports_data,cti_tta):
    df = pd.read_csv(reports_data)
    final_df = pd.DataFrame()
    final_df["URL"] = df["link"]
    final_df["Text"] = df["rapport"]
    final_df["GT"] = df["group_name"]
    final_df.to_csv(cti_tta)
 