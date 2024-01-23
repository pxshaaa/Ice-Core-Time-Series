# Teddy Tonin and Pasha Alidadi

from cmath import nan
import pandas as pd

# This module is composed of tools useful to read the data 

# Detects file's header

def detect_header(filepath):
    if filepath.endswith('.xlsx'):
        df = pd.read_excel(filepath, header=None)
    else:
        df = pd.read_csv(filepath, header=None, sep='\t')

    for i, row in enumerate(df.values):
        # Check if the first cell is not NaN and the second cell is a string ###but make sure that you use notna function!!!
        if pd.notna(row[0]) and isinstance(row[1], str):
            return i  # Return the index of the header row
        if i == 10:
            break  # Stop after checking 10 rows

    return 0  # Default to the first row as the header if no header is detected


def read_data(filepath):
    if filepath.endswith('.xlsx'):
        # Excel file
        dtype_dict = {col_name: str for col_name in pd.read_excel(filepath, nrows=detect_header(filepath))}
        df = pd.read_excel(filepath, header=detect_header(filepath), dtype=dtype_dict)
        
        # Convert the DataFrame to a .txt file, because the program does not work with xlsx files
        txt_filepath = filepath.rsplit('.', 1)[0] + '.txt'  # Change the file extension to .txt
        df.to_csv(txt_filepath, sep='\t', index=False, header=True)  # Save as a tab-delimited .txt file
        
        print(f"Converted Excel file to {txt_filepath}")
        df = df.dropna(axis=1, how='all')
        return df  # Return the DataFrame for further processing
    else:
        # any other file
        dtype_dict = {col_name: str for col_name in pd.read_csv(filepath, nrows= detect_header(filepath))}
        df = pd.read_csv(filepath, header=detect_header(filepath), sep='\t', dtype=dtype_dict)
    
    ### Drop columns where all values are NaN
    df = df.dropna(axis=1, how='all')
    return df

def titlecolumns(df):
    columns = df.columns.tolist()
    return columns
