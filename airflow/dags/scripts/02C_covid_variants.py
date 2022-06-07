import pandas as pd
import numpy as np
import json
import requests

data = requests.get("http://github.com/hodcroftlab/covariants/raw/master/cluster_tables/USAClusters_data.json").json()

def parse_variants_json(data):
    df_list = []
    for state, data in data["countries"].items():
        df_state = pd.DataFrame.from_dict(data) 

        df_state = df_state.melt(
            id_vars="week", 
            value_vars=[ c for c in df_state.columns if c != "week" and c != "total_sequences" ],
            var_name="variant",
            value_name="cases"
        ).rename(columns={"week": "date"})
        
        df_state.insert(0, "state", state)

        df_list.append(df_state)

    return pd.concat(df_list)

df_full = parse_variants_json(data)
print(df_full.shape)
df_full.head()
df_full.to_parquet("../../data/variants.parquet", engine="pyarrow", compression="brotli")

