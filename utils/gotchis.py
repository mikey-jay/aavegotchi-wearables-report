import datetime
import pandas as pd
from utils.subgraph import get_core_matic_query, get_subgraph_result_df
import utils.database as db
from utils.config import UPDATE_TIME

GOTCHIS_TABLE_NAME = 'gotchis'

def get_gotchis_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(GOTCHIS_TABLE_NAME):
        gotchis_df = get_gotchis_from_subgraph()
        store_gotchis_to_database(gotchis_df)
    else:
        gotchis_df = get_gotchis_from_database()    
    return gotchis_df

def get_gotchis_from_database() -> pd.DataFrame:
    return db.get_df_from_database(GOTCHIS_TABLE_NAME).set_index('id')

def store_gotchis_to_database(df: pd.DataFrame):
    return db.store_df_to_database(GOTCHIS_TABLE_NAME, df)

def get_gotchis_from_subgraph():
    gotchis_query = get_core_matic_query(
        { 'aavegotchis': {
            'params': { 'where': { 'status': 3 } },
            'fields': ["id", { "originalOwner": { 'fields': ['id']} }, "name"] }}
    )
    gotchis_result = gotchis_query.execute(False)
    gotchis_df = get_subgraph_result_df(gotchis_result)
    return gotchis_df

