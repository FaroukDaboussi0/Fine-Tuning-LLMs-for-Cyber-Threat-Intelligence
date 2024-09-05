import os
import pandas as pd
import random
from AIDataAugment.TextAugmentor import TextAugmentor

def preprocess_df(df):
    """Preprocesses a DataFrame by normalizing column names, adjusting QSM, and shuffling options."""
    if df is None:
        return None

    df = df.dropna()
    df = normalize_column_names(df)
    df = adjust_qsm(df)
   
    return df



def adjust_qsm(df):
    """Extracts the last character of the 'Correct Answer' column as the QSM."""
    if df is None:
        return None

    def get_last_char(s):
        if isinstance(s, str) and s.strip():
            return s.split()[-1][-1]
        return None

    df['Correct Answer'] = df['Correct Answer'].apply(get_last_char, inplace=True)  # Modify original column
    return df
def normalize_column_names(df):
    """Normalizes column names by renaming the first column to 'Reference'."""
    if df.columns.size > 0:
        df.loc[:, df.columns[0]] = 'Reference'  # Assign directly to first column
    else:
        print("Warning: DataFrame has no columns to rename.")
    return df

def adjust_qsm(df):
    """Adjusts the 'Correct Answer' column by replacing specific options with single characters."""
    if df is None:
        return None
    
    def map_options(value):
        mapping = {
            'Option A': 'A',
            'Option B': 'B',
            'Option C': 'C',
            'Option D': 'D'
        }
        return mapping.get(value, value)  # Return the mapped value if it exists, otherwise return the original value
    
    # Apply the mapping function to the 'Correct Answer' column
    df.loc[:, 'Correct Answer'] = df['Correct Answer'].apply(map_options)
    
    return df





def shuffle_options(df):
    """Shuffles answer options and adjusts the correct answer accordingly."""
    if df is None:
        return None

    options = ["Option A", "Option B", "Option C", "Option D"]

    def shuffle_row(row):
        correct_answer = row.get("Correct Answer", None)
        if correct_answer is None:
            return row

        original_options = {opt: row[opt] for opt in options}
        shuffled_options = options[:]
        random.shuffle(shuffled_options)

        for i, opt in enumerate(shuffled_options):
            row[options[i]] = original_options[opt]

        for opt in options:
            if original_options.get(opt) == row.get(f"Option {correct_answer}", None):
                row["Correct Answer"] = opt.split()[1]
                break

        return row

    return df.apply(shuffle_row, axis=1)

def augment_data(df, max_len, column_to_augment="Question"):
    """Augments the DataFrame based on the maximum length of other DataFrames."""
    if df is None or max_len <= 0 or len(df) == 0:
        return df
    print(max_len)
    augmentation_factor = max_len // len(df)  - 1
    print(len(df))
    print(augmentation_factor)
    if augmentation_factor > 0:
        augmentor = TextAugmentor(api_key=os.environ.get('GOOGLE_API_KEY'))
        aug_df = augmentor.augment(
            dataframe=df,
            column_to_augment=column_to_augment,
            total_augmentations=int(augmentation_factor),
            output_filename=None
        )
        df = pd.concat([df, aug_df]).reset_index(drop=True)
    return df

def balance_data(list_of_json):
    import pandas as pd
    import random
    from AIDataAugment.TextAugmentor import TextAugmentor


    #problem with json to df
    #here
    dataframes = [pd.read_json(file) for file in list_of_json]
    #---------------------------------

    
    allowed_values = ['Option C', 'Option D', 'Option A', 'Option B']
    finaldf = pd.DataFrame()
    new_column_names = ["Reference","Question",	"Option A","Option B", "Option C", "Option D","Correct Answer"	,"Explanation"]  

    max_length = max(len(df) for df in dataframes if df is not None)

    for df in dataframes:
        if df is not None:
            # Filter rows based on 'Correct Answer' values
            df = df[df["Correct Answer"].apply(lambda x: isinstance(x, int) or x in allowed_values)]
            
            # Preprocess the DataFrame
            df = preprocess_df(df)
            
            # Rename columns based on index
            df.columns = [new_column_names[i] if i < len(new_column_names) else df.columns[i] for i in range(len(df.columns))]
            
            # Augment data
            df = augment_data(df, max_length)
            
            # Concatenate to final DataFrame
            finaldf = pd.concat([finaldf, df], ignore_index=True)

        # Shuffle the options in the final DataFrame
        finaldf = shuffle_options(finaldf)


    return finaldf

