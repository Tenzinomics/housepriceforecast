import pandas as pd

#input for this is (dataframe, dictionary for the lagg values)
def data_process_tinator(df,var_lagg_values):
    for var in var_lagg_values:

        lagg_value = var_lagg_values[var]

        df[var] = df[var].shift(periods=-lagg_value)
        
    df_processed = df.dropna()

    return df_processed
