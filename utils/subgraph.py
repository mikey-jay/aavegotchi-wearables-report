import pandas as pd
import time
import math
import os
from dotenv import load_dotenv
from subgraph.query import SubgraphQuery

# Load environment variables
load_dotenv()

AAVEGOTCHI_CORE_MATIC = os.getenv("AAVEGOTCHI_CORE_MATIC_URL")
FORGE_SUBGRAPH_URL = os.getenv("FORGE_SUBGRAPH_URL")

def get_subgraph_result_df(result_obj, id_index=True):
    df = pd.DataFrame(pd.json_normalize(result_obj))
    if (id_index & ('id' in df.columns)):
        df.set_index('id', inplace=True)
    return df

def get_core_matic_query(query_str):
    return SubgraphQuery(AAVEGOTCHI_CORE_MATIC, query_str)

def get_forge_query(query_str):
    return SubgraphQuery(FORGE_SUBGRAPH_URL, query_str)

def round_time_to_nearest_minutes(minutes=1, precise_time=time.time()):
    return math.floor(precise_time / (60 * minutes)) * (60 * minutes)

def days_ago(days):
    return round(time.time() - (days * 24 * 60 * 60))