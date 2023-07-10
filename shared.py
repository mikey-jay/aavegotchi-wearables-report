from utils.config import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import math
from subgraph.query import SubgraphQuery
from utils.subgraph import get_core_matic_query, get_subgraph_result_df
import datetime
import os
import json
from itables import show
import itables.options
from IPython.core.display import Markdown as md
from charts.grouped_bar_chart import GroupedBarChart
from charts.chart_collection import ChartCollection, ChartBuilder
from charts.chart_renderer import ChartRenderer
from utils.wearable_types import get_wearable_types_df
from utils.wearable_purchases import get_wearable_purchases_df

NAVIGATION_PAGES = [
    { 'title': 'Volume', 'file': 'dashboard_volume.ipynb', 'description': 'Baazaar sales volume for wearables' },
    { 'title': 'Prices', 'file': 'dashboard_price.ipynb', 'description': 'Median sale prices and market capitalization' },
    { 'title': 'Supply', 'file': 'dashboard_supply.ipynb', 'description': 'Available supply and trait distribution of wearables' },
    { 'title': 'Usage', 'file': 'dashboard_usage_rf.ipynb', 'description': 'Equipping of wearables for rarity farming' },
]

# setup matplotlib
plt.style.use('seaborn-whitegrid')


# setup itables
itables.options.paging = False # type: ignore
itables.options.columnDefs = [{"className": "dt-left", "targets": [0]}] # type: ignore
itables.options.dom = ITABLE_DOM_SHORT # type: ignore
itables.options.maxBytes = 0 # disable itable size limit

get_rarity_sort_value = lambda rarity: list(RARITY_SCORE_MODIFIERS.values()).index(rarity)

# bar charts
def get_bar_charts(df, category, metrics, colors):
    fig, axes = plt.subplots(len(metrics))
    fig.set_size_inches(12,6 * len(metrics))
    for row in range(0,len(metrics)):
        m = metrics[row]
        ax = axes[row] if len(metrics) > 1 else axes
        annotate_bars(ax.bar(df[category], df[m], color=colors[row]), ax) # type: ignore
        ax.set_title('{m}'.format(m=m)) # type: ignore

def annotate_bars(bars, ax, format='{:,.0f}', rotation=0):
    for b in bars:
        height = b.get_height()
        ax.annotate(format.format(height),
        xy=(b.get_x() + b.get_width() / 2, height + b.get_y()),
        xytext=(0, 3), # 3 points vertical offset
        textcoords="offset points",
        ha='center', va='bottom', rotation=rotation)       

def show_itable(df, order=[[0, 'asc']], dom=ITABLE_DOM_SHORT, title='', precision=0, column_formats={}):
    formatted_df = df.copy()
    default_number_format = "{{:,.{precision}f}}".format(precision=precision)
    for column in df.columns:
        if column in column_formats:
            formatted_df[column] = df[column].apply(column_formats[column].format)
        elif df[column].dtype.kind in 'if' and column not in column_formats:
            formatted_df[column] = df[column].apply(default_number_format.format)
        
    return show(formatted_df, order=order, paging=(True if dom == ITABLE_DOM_LONG else False), dom=dom, tags=get_table_title(title))

def show_itable_long(df, order=[[0, 'asc']], **args):
    return show_itable(df, order, ITABLE_DOM_LONG, **args)

def get_page_header():
    get_readable_time = lambda ts: datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    return (md("\nUsing data from {start} to {end} UTC".format(start=get_readable_time(START_TIME), end=get_readable_time(END_TIME - 1))))

def get_table_title(title):
    return ('<caption style="caption-side: top; text-align: left; font-size: 150%; margin-top: 1em; ">' + title + '</caption>') if title else ''

rarity_color_mappings = {
    'common': 'mediumslateblue',
    'uncommon': 'darkturquoise',
    'rare': 'deepskyblue',
    'legendary': 'orange',
    'mythical': 'hotpink',
    'godlike': 'mediumspringgreen'
}

get_rarity_color = lambda rarity: rarity_color_mappings[rarity]

def get_gotchis_wearables_df(block):
    local_db_file = 'data/gotchi_wearables_{b}.csv'.format(b=block)
    db_exists = os.path.exists(local_db_file)
    
    if (db_exists):
        gotchis_wearables_df = pd.read_csv(local_db_file, index_col='id')
        gotchis_wearables_df['equippedWearables'] = gotchis_wearables_df['equippedWearables'].apply(json.loads)
    else:
        gotchis_query = get_core_matic_query(
            { 'aavegotchis': {
                'params': { 'block': { 'number': block }, 'where': { 'status': 3 } },
                'fields': ["id", { "owner": { 'fields': ['id']} }, "equippedWearables"] }}
        )
        gotchis_result = gotchis_query.execute(False)
        gotchis_wearables_df = get_subgraph_result_df(gotchis_result)
        gotchis_wearables_df.to_csv(local_db_file)
    
    has_wearables = list(map(any, gotchis_wearables_df['equippedWearables'].to_list()))
    return gotchis_wearables_df[has_wearables]

def get_wearable_equipped_df(gotchis_df, types_df):
    has_wearable_equipped = lambda id: list(map(lambda w: id in w, gotchis_df['equippedWearables'].to_list()))
    get_wearable_equipped_count = lambda id: sum(has_wearable_equipped(id))
    get_unique_owner_count = lambda id: gotchis_df[has_wearable_equipped(id)]['owner.id'].nunique()
    equipped_df = pd.DataFrame(types_df.index.map(get_wearable_equipped_count).rename('equippedCount'), types_df.index)
    owner_equipped_df = equipped_df.join(pd.DataFrame(types_df.index.map(get_unique_owner_count).rename('ownerCount'), types_df.index))
    return owner_equipped_df

def get_seconds_since_modified(filename):
    full_path = os.path.abspath(filename)
    return time.time() - os.path.getmtime(full_path)

def get_wearables_purchases_types_df(types_df, purchases_df):
    types_merge_columns = ['name', 'rarity', 'slotNames', 'NRG Effect', 'AGG Effect', 'SPK Effect', 'BRN Effect']
    purchases_types_df = purchases_df.merge(types_df[types_merge_columns], how="left", left_on='erc1155TypeId', right_index=True)
    return purchases_types_df

def get_wearables_market_cap_df(types_df, purchases_df):
    last_price = purchases_df.groupby('erc1155TypeId').last(1)['price'].rename('lastPrice')
    market_cap_df = types_df.join(last_price).fillna(0)
    market_cap_df['marketCap'] = market_cap_df['lastPrice'] * market_cap_df['maxQuantity']
    return market_cap_df