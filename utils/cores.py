import pandas as pd
import numpy as np

# cores need to be manually updated as their supply is not indexed in the subgraph

def get_core_supply_df():
    core_supply_df = pd.read_csv('data/core_supply.csv')
    core_supply_df['Supply'] = core_supply_df['Supply'].astype(np.int64)
    return core_supply_df