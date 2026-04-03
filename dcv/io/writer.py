import pandas as pd


def write_file(df, filepath):
    if filepath.endswith(".csv"):
        df.to_csv(filepath, index=False)
    elif filepath.endswith(".xlsx"):
        df.to_excel(filepath, index=False)
    else:
        raise ValueError("Unsupported file format")
