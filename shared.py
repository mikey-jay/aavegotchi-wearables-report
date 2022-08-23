from main import *

# project-specific code goes here
import datetime

ITEM_TYPE_CATEGORY_WEARABLE = 0
UPDATE_TIME = 1660745008 # Aug 17 approx 10 AM
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
START_TIME = END_TIME - TIME_RANGE_SECONDS
QUERY_TIME_INTERVAL = 30 * SECONDS_IN_A_DAY # break up the query into 30 day chunks
EXCLUDE_WEARABLE_IDS = [0, 162] # exclude the void and Miami Shirt (never minted)

def get_time_intervals(start, end, step):
    while start <= end:
        yield start
        start += step

def get_first_day_of_week(d):
    weekday = d.isocalendar().weekday - 1
    return d - datetime.timedelta(days=weekday)

def get_wearable_purchases_df():

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
    purchases_df['price'] = purchases_df['priceInWei'] / WEI_PER_ETH
    purchases_df['totalPrice'] = purchases_df['price'] * purchases_df['quantity']

    purchases_df.drop(['timeLastPurchased', 'priceInWei'], axis=1, inplace=True)
    purchases_df.sort_values('timePurchased', inplace=True)
    return purchases_df

def get_wearable_types_df():
    
    wearables_query = get_core_matic_query(
    { 'itemTypes': {
        'params': { 'where': { 'category': ITEM_TYPE_CATEGORY_WEARABLE, 'id_not': UPDATE_TIME_HASH, 'id_not_in': EXCLUDE_WEARABLE_IDS, 'canBeTransferred': True } },
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
