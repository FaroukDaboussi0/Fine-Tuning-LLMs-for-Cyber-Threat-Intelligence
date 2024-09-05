import os
from AIDataAugment.TextAugmentor import TextAugmentor
import pandas as pd

def balance_train_data(cti_rcm , cti_vsp , cti_mcq,cti_tta):


    saving_cti_tta = r'Data\finetuning_data\balanced_data\cti_tta.csv'
   

    cti_mcq_data = pd.read_csv(cti_mcq)
    cti_tta_data = pd.read_csv(cti_tta)

    
    cti_tta_data = cti_tta_data.drop(cti_tta_data.columns[0], axis=1)

    limit = len(cti_mcq_data)


    column_to_augment = "Text"
    augmentor = TextAugmentor(api_key=os.environ.get('GOOGLE_API_KEY'))
    augmentor.augment(
        dataframe=cti_tta_data,
        column_to_augment=column_to_augment,
        total_augmentations=int(limit/cti_tta_data),
        output_filename=saving_cti_tta
        )

    return None
