import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from subgraph.query import SubgraphQuery
from shared import *

AAVEGOTCHI_CORE_MATIC = "https://api.thegraph.com/subgraphs/name/aavegotchi/aavegotchi-core-matic"

def get_subgraph_result_df(result_obj, id_index=True):
    df = pd.DataFrame(pd.json_normalize(result_obj))
    if (id_index):
        df.set_index('id', inplace=True)
    return df

def get_core_matic_query(query_str):
    return SubgraphQuery(AAVEGOTCHI_CORE_MATIC, query_str)

def round_time_to_nearest_minutes(minutes=1, precise_time=time.time()):
    return math.floor(precise_time / (60 * minutes)) * (60 * minutes)

def days_ago(days):
    return round(time.time() - (days * 24 * 60 * 60))