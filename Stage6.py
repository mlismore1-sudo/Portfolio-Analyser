def dataframe_to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")
