from main import *

# project-specific code goes here
import datetime
import calendar
import os
import json
from itables import show
import itables.options
from IPython.display import Markdown as md

def get_midnight_utc_today():
    utc_now_struct = time.gmtime()
    return int(calendar.timegm(datetime.datetime(utc_now_struct.tm_year, utc_now_struct.tm_mon, utc_now_struct.tm_mday, 0, 0, 0, 0, datetime.timezone.utc).timetuple()))

def get_first_of_month_utc(unix_time):
    utc_struct = time.gmtime(unix_time)
    return int(calendar.timegm(datetime.datetime(utc_struct.tm_year, utc_struct.tm_mon, 1, 0, 0, 0, 0, datetime.timezone.utc).timetuple()))

ITEM_TYPE_CATEGORY_WEARABLE = 0
UPDATE_TIME = get_midnight_utc_today()
WEI_PER_ETH = 10 ** 18
USE_CACHE = True
TRAIT_NAMES = ['NRG', 'AGG', 'SPK', 'BRN', 'EYS', 'EYC']
SLOT_POSITION_NAMES = ['Body', 'Face', 'Eyes', 'Head', 'Hand L', 'Hand R', 'Pet', 'BG']
RARITY_SCORE_MODIFIERS = { 1: 'common', 2: 'uncommon', 5: 'rare', 10: 'legendary', 20: 'mythical', 50: 'godlike'  }
UPDATE_TIME_HASH = hex(hash(UPDATE_TIME))
TIME_RANGE_DAYS = 365
SECONDS_IN_A_DAY = 24 * 60 * 60
TIME_RANGE_SECONDS = TIME_RANGE_DAYS * SECONDS_IN_A_DAY
END_TIME = UPDATE_TIME
START_TIME = get_first_of_month_utc(END_TIME - TIME_RANGE_SECONDS)
QUERY_TIME_INTERVAL = 30 * SECONDS_IN_A_DAY # break up the query into 30 day chunks
EXCLUDE_WEARABLE_IDS = [0, 162] # exclude the void and Miami Shirt (never minted)
RARITY_FARMING_BLOCKS = [14082019, 20633780, 25806269, 31770753] # adjusted blocks for subgraph error with rf szn 2-3 20633778, 25806267
ITABLE_DOM_LONG = "lftipr"
ITABLE_DOM_SHORT = "tr"
GHST_COLOR = 'magenta'
DEFAULT_COLOR = 'royalBlue'

NAVIGATION_PAGES = [
    { 'title': 'Volume', 'file': 'dashboard_volume.ipynb', 'description': 'Baazaar sales volume for wearables' },
    { 'title': 'Prices', 'file': 'dashboard_price.ipynb', 'description': 'Median sale prices and market capitalization' },
    { 'title': 'Supply', 'file': 'dashboard_supply.ipynb', 'description': 'Available supply and trait distribution of wearables' },
    { 'title': 'Usage', 'file': 'dashboard_usage_rf.ipynb', 'description': 'Equipping of wearables for rarity farming' },
]

# setup matplotlib
plt.style.use('seaborn-whitegrid')

# pandas options
pd.set_option("styler.format.thousands", ",")

# setup itables
itables.options.paging = False
itables.options.columnDefs = [{"className": "dt-left", "targets": [0]}]
itables.options.dom = ITABLE_DOM_SHORT

# bar charts
def get_bar_charts(df, category, metrics, colors):
    fig, axes = plt.subplots(len(metrics))
    fig.set_size_inches(12,6 * len(metrics))
    for row in range(0,len(metrics)):
        m = metrics[row]
        ax = axes[row] if len(metrics) > 1 else axes
        annotate_bars(ax.bar(df[category], df[m], color=colors[row]), ax)
        ax.set_title('{m}'.format(m=m))

def annotate_bars(bars, ax, format='{:,.0f}'):
    for b in bars:
        height = b.get_height()
        ax.annotate(format.format(height),
        xy=(b.get_x() + b.get_width() / 2, height + b.get_y()),
        xytext=(0, 3), # 3 points vertical offset
        textcoords="offset points",
        ha='center', va='bottom')       

def show_itable(df, order=[[0, 'asc']], dom=ITABLE_DOM_SHORT, title=''):
    with pd.option_context("display.float_format", "{:,.0f}".format):
        return show(df.astype('float64',errors='ignore'), order=order, paging=(True if dom == ITABLE_DOM_LONG else False), dom=dom, tags=get_table_title(title))

def show_itable_long(df, order):
    return show_itable(df, order, ITABLE_DOM_LONG)

def get_page_header():
    get_readable_time = lambda ts: datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
    return (md("\nUsing data from {start} to {end} UTC".format(start=get_readable_time(START_TIME), end=get_readable_time(END_TIME - 1))))

def get_table_title(title):
    return ('<caption style="caption-side: top; text-align: left; font-size: 150%; margin-top: 1em; ">' + title + '</caption>') if title else ''

def get_time_intervals(start, end, step):
    while start <= end:
        yield start
        start += step

get_rarity_color = lambda rarity: {
    'common': 'mediumslateblue',
    'uncommon': 'darkturquoise',
    'rare': 'deepskyblue',
    'legendary': 'orange',
    'mythical': 'hotpink',
    'godlike': 'mediumspringgreen'
}[rarity]

def get_first_day_of_week(d):
    weekday = d.isocalendar().weekday - 1
    return d - datetime.timedelta(days=weekday)

def get_wearable_purchases_df():

    local_db_file = 'db/wearable_purchases.csv'

    db_exists = os.path.exists(local_db_file)
    last_db_purchase_time = 0

    if db_exists:
        db_modified_time = os.path.getmtime(os.path.abspath(local_db_file))
        db_expired = db_modified_time <= UPDATE_TIME
        purchases_df = pd.read_csv(local_db_file, index_col='id').fillna('')
        last_db_purchase_time = round(purchases_df['timeLastPurchased'].astype(np.int64).max())
    else:
        db_expired = True
        purchases_df = pd.DataFrame()

    if db_expired:
        purchases_result = []
        for interval_start in get_time_intervals(max(START_TIME, last_db_purchase_time + 1), END_TIME, QUERY_TIME_INTERVAL):
            interval_end = min(interval_start + QUERY_TIME_INTERVAL, END_TIME)
            purchases_query = get_core_matic_query(
                { 'erc1155Purchases': {
                    'params': { 'where': { 'category': ITEM_TYPE_CATEGORY_WEARABLE, 'timeLastPurchased_lt': interval_end, 'timeLastPurchased_gte': interval_start } },
                    'fields': ["id", "listingID", "erc1155TypeId", "priceInWei", "quantity", "timeLastPurchased"] }}
            )
            purchases_result += purchases_query.execute(USE_CACHE)
        purchases_df = pd.concat([purchases_df, get_subgraph_result_df(purchases_result)])
        purchases_df.to_csv(local_db_file)

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
    purchases_df['price'] = purchases_df['priceInWei'] / WEI_PER_ETH
    purchases_df['totalPrice'] = purchases_df['price'] * purchases_df['quantity']

    purchases_df.drop(['timeLastPurchased', 'priceInWei'], axis=1, inplace=True)
    purchases_df.sort_values('timePurchased', inplace=True)
    return purchases_df

def get_wearable_types_df():
    
    wearables_query = get_core_matic_query(
    { 'itemTypes': {
        'params': { 'where': { 'category': ITEM_TYPE_CATEGORY_WEARABLE, 'id_not': UPDATE_TIME_HASH, 'id_not_in': list(map(str, EXCLUDE_WEARABLE_IDS)), 'canBeTransferred': True } },
        'fields': ["id", "name", "traitModifiers", "slotPositions", "maxQuantity", "rarityScoreModifier"] }}
    )

    wearables_result = wearables_query.execute(USE_CACHE)
    wearable_types_df = get_subgraph_result_df(wearables_result)
    wearable_types_df.set_index(wearable_types_df.index.astype(np.int64), inplace=True)
    wearable_types_df.sort_index(inplace=True)
    item_types_int_fields = ['maxQuantity', 'rarityScoreModifier']
    wearable_types_df[item_types_int_fields] = wearable_types_df[item_types_int_fields].astype(np.int64)

    # trait modifiers
    append = lambda s2: lambda s1: str(s1) + str(s2)
    traitEffectColumns = list(map(append(' Effect'), TRAIT_NAMES))
    getTraitEffect = lambda s: pd.Series(s).apply(lambda modifier: '+' if modifier > 0 else '-' if modifier < 0 else '')
    wearable_types_df[TRAIT_NAMES] = wearable_types_df['traitModifiers'].apply(pd.Series)
    wearable_types_df[traitEffectColumns] = wearable_types_df['traitModifiers'].apply(getTraitEffect)
    wearable_types_df.drop(['traitModifiers', 'EYS', 'EYC', 'EYS Effect', 'EYC Effect'], axis=1, inplace=True)

    # slot positions
    def get_slot_name_if_true(t):
        i, has_slot = t
        return SLOT_POSITION_NAMES[i] if has_slot else ''
    is_not_empty = lambda x: x != ''
    get_slot_names = lambda row: ', '.join(filter(is_not_empty, list(map(get_slot_name_if_true, enumerate(row)))))
    wearable_types_df['slotNames'] = wearable_types_df['slotPositions'].apply(get_slot_names)
    wearable_types_df.drop('slotPositions', axis=1, inplace=True)

    # rarity
    wearable_types_df['rarity'] = wearable_types_df['rarityScoreModifier'].apply(lambda x: RARITY_SCORE_MODIFIERS[x])

    return wearable_types_df

def get_gotchis_wearables_df(block):
    local_db_file = 'db/gotchi_wearables_{b}.csv'.format(b=block)
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
        gotchis_result = gotchis_query.execute(USE_CACHE)
        gotchis_wearables_df = get_subgraph_result_df(gotchis_result)
        gotchis_wearables_df.to_csv(local_db_file)
    
    has_wearables = list(map(any, gotchis_wearables_df['equippedWearables'].to_list()))
    return gotchis_wearables_df[has_wearables]

def get_wearable_equipped_df(block, gotchis_df, types_df):
    #gotchis_df = get_gotchis_wearables_df(block)
    #types_df = get_wearable_types_df()
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
    purchases_df = get_wearable_purchases_df()
    #types_df = get_wearable_types_df()
    types_merge_columns = ['name', 'rarity', 'slotNames', 'NRG Effect', 'AGG Effect', 'SPK Effect', 'BRN Effect']
    purchases_types_df = purchases_df.merge(types_df[types_merge_columns], how="left", left_on='erc1155TypeId', right_index=True)
    return purchases_types_df

def get_wearables_market_cap_df(types_df, purchases_df):
    last_price = purchases_df.groupby('erc1155TypeId').last(1)['price'].rename('lastPrice')
    market_cap_df = types_df.join(last_price).fillna(0)
    market_cap_df['marketCap'] = market_cap_df['lastPrice'] * market_cap_df['maxQuantity']
    market_cap_df
    return market_cap_df