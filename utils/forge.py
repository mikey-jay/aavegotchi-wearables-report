import utils.database as db
import datetime
import pandas as pd
import numpy as np
from utils.subgraph import get_forge_query, get_subgraph_result_df
from utils.config import START_TIME, END_TIME, QUERY_TIME_INTERVAL, ITEM_TYPE_CATEGORY_WEARABLE, USE_CACHE, WEI_PER_ETH, UPDATE_TIME
from utils.time_utils import get_first_day_of_week, get_time_intervals

# forge activity

FORGE_ACTIVITY_TABLE_NAME = 'forge_activity'

def get_forge_activity_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(FORGE_ACTIVITY_TABLE_NAME):
        forge_activity_df = get_forge_activity_from_subgraph()
        store_forge_activity_to_database(forge_activity_df)
    else:
        forge_activity_df = get_forge_activity_from_database()    
    return forge_activity_df

def store_forge_activity_to_database(df: pd.DataFrame):
    return db.store_df_to_database(FORGE_ACTIVITY_TABLE_NAME, df)

def get_forge_activity_from_database() -> pd.DataFrame:
    return db.get_df_from_database(FORGE_ACTIVITY_TABLE_NAME).set_index('id')

def get_forge_activity_from_subgraph():
    forge_activity_result = []

    for entity in ['itemForgeds', 'itemSmelteds']:

        entity_result = []
        
        for interval_start in get_time_intervals(START_TIME, END_TIME, QUERY_TIME_INTERVAL):
            interval_end = min(interval_start + QUERY_TIME_INTERVAL, END_TIME)
            entity_query = get_forge_query(
                {
                    entity: {
                    'params': { 'where': { 'timestamp_lt': interval_end, 'timestamp_gte': interval_start } },
                    'fields': [
                        "id",
                        { 'item': { 'fields': ['id'] } },
                        { 'gotchi': { 'fields': ['id'] } },
                        "timestamp"
                    ]}
                }
            )
            entity_result += entity_query.execute(USE_CACHE)

        for item in entity_result:
            item['activity'] = entity
            forge_activity_result.append(item)

    forge_activity_df = get_subgraph_result_df(forge_activity_result)
    int_fields = ['item.id', 'gotchi.id']
    forge_activity_df[int_fields] = forge_activity_df[int_fields].astype(np.int64)
    forge_activity_df['time'] = pd.to_datetime(forge_activity_df['timestamp'], unit="s", utc=True)
    forge_activity_df['date'] = forge_activity_df['time'].dt.date
    forge_activity_df['startOfWeek'] = list(map(get_first_day_of_week, forge_activity_df['date'].tolist()))
    forge_activity_df['yearMonth'] = forge_activity_df['date'].astype(str).apply(lambda d: d[0:7])
    forge_activity_df.drop(['timestamp'], axis=1, inplace=True)
    forge_activity_df.sort_values('time', inplace=True)
    return forge_activity_df

# smithing skill

SMITHING_SKILL_TABLE_NAME = 'smithing_skill'

def get_smithing_skill_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(SMITHING_SKILL_TABLE_NAME):
        smithing_skill_df = get_smithing_skill_from_subgraph()
        store_smithing_skill_to_database(smithing_skill_df)
    else:
        smithing_skill_df = get_smithing_skill_from_database()    
    return smithing_skill_df

def store_smithing_skill_to_database(df: pd.DataFrame):
    return db.store_df_to_database(SMITHING_SKILL_TABLE_NAME, df)

def get_smithing_skill_from_database() -> pd.DataFrame:
    return db.get_df_from_database(SMITHING_SKILL_TABLE_NAME).set_index('id')

def get_smithing_skill_from_subgraph():
    smithing_skill_query = get_forge_query(
        {
            'gotchis': {
            'fields': [
                "id",
                "skillPoints",
                "smithingLevel"
            ]}
        }
    )
    smithing_skill_result = smithing_skill_query.execute(USE_CACHE)
    smithing_skill_df = get_subgraph_result_df(smithing_skill_result)
    int_fields = ['skillPoints', 'smithingLevel']
    smithing_skill_df[int_fields] = smithing_skill_df[int_fields].astype(np.int64)
    smithing_skill_df.sort_values('smithingLevel', inplace=True, ascending=False)
    return smithing_skill_df

# forge items

FORGE_ITEMS_TABLE_NAME = "forge_items"

def get_forge_items_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(FORGE_ITEMS_TABLE_NAME):
        forge_items_df = get_forge_items_from_subgraph()
        store_forge_items_to_database(forge_items_df)
    else:
        forge_items_df = get_forge_items_from_database()    
    return forge_items_df

def store_forge_items_to_database(df: pd.DataFrame):
    return db.store_df_to_database(FORGE_ITEMS_TABLE_NAME, df)

def get_forge_items_from_database() -> pd.DataFrame:
    return db.get_df_from_database(FORGE_ITEMS_TABLE_NAME).set_index('id')

def get_forge_items_from_subgraph():
    forge_item_query = get_forge_query(
        {
            'items': {
            'fields': [
                "id",
                "timesForged",
                "timesSmelted"
            ]}
        }
    )
    forge_items_result = forge_item_query.execute(USE_CACHE)
    forge_items_df = get_subgraph_result_df(forge_items_result)
    int_fields = ['timesForged', 'timesSmelted']
    forge_items_df[int_fields] = forge_items_df[int_fields].astype(np.int64)
    forge_items_df['change_in_supply'] = forge_items_df['timesForged'] - forge_items_df['timesSmelted']
    forge_items_df.sort_index(inplace=True)
    return forge_items_df