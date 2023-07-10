import utils.database as db
import datetime
import pandas as pd
import numpy as np
from utils.subgraph import get_core_matic_query, get_subgraph_result_df
from utils.config import START_TIME, END_TIME, QUERY_TIME_INTERVAL, ITEM_TYPE_CATEGORY_WEARABLE, USE_CACHE, WEI_PER_ETH, UPDATE_TIME
from utils.time_utils import get_first_day_of_week, get_time_intervals

WEARABLE_PURCHASES_TABLE_NAME = 'wearable_purchases'

def get_wearable_purchases_from_database() -> pd.DataFrame:
    return db.get_df_from_database(WEARABLE_PURCHASES_TABLE_NAME).set_index('id')

def store_wearable_purchases_to_database(df: pd.DataFrame):
    return db.store_df_to_database(WEARABLE_PURCHASES_TABLE_NAME, df)

def get_wearable_purchases_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(WEARABLE_PURCHASES_TABLE_NAME):
        wearable_purchases_df = get_wearable_purchases_from_subgraph()
        store_wearable_purchases_to_database(wearable_purchases_df)
    else:
        wearable_purchases_df = get_wearable_purchases_from_database()    
    return wearable_purchases_df

def get_wearable_purchases_from_subgraph():

    purchases_result = []
    for interval_start in get_time_intervals(START_TIME, END_TIME, QUERY_TIME_INTERVAL):
        interval_end = min(interval_start + QUERY_TIME_INTERVAL, END_TIME)
        purchases_query = get_core_matic_query(
            { 'erc1155Purchases': {
                'params': { 'where': { 'category': ITEM_TYPE_CATEGORY_WEARABLE, 'timeLastPurchased_lt': interval_end, 'timeLastPurchased_gte': interval_start } },
                'fields': ["id", "listingID", "erc1155TypeId", "priceInWei", "quantity", "timeLastPurchased"] }}
        )
        purchases_result += purchases_query.execute(USE_CACHE)
    purchases_df = get_subgraph_result_df(purchases_result)

    # data types
    purchases_int_fields = ['listingID', 'erc1155TypeId', 'quantity', 'timeLastPurchased']
    purchases_df[purchases_int_fields] = purchases_df[purchases_int_fields].astype(np.int64)
    purchases_df['priceInWei'] = purchases_df['priceInWei'].astype(np.longdouble)

    # time intervals
    purchases_df['timePurchased'] = pd.to_datetime(purchases_df['timeLastPurchased'], unit="s", utc=True)
    purchases_df['datePurchased'] = purchases_df['timePurchased'].dt.date
    purchases_df['startOfWeekPurchased'] = list(map(get_first_day_of_week, purchases_df['datePurchased'].tolist()))
    purchases_df['yearMonthPurchased'] = purchases_df['datePurchased'].astype(str).apply(lambda d: d[0:7])

    # prices
    purchases_df['price'] = (purchases_df['priceInWei'] / WEI_PER_ETH).astype(np.float64)
    purchases_df['totalPrice'] = purchases_df['price'] * purchases_df['quantity']

    purchases_df.drop(['timeLastPurchased', 'priceInWei'], axis=1, inplace=True)
    purchases_df.sort_values('timePurchased', inplace=True)
    return purchases_df