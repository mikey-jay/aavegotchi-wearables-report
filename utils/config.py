from utils.time_utils import get_midnight_utc_today, get_first_of_month_utc

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
RARITY_FARMING_BLOCKS = [14082019, 20633780, 25806269, 31770753, 39284410, 44479233] # adjusted blocks for subgraph error with rf szn 2-3 20633778, 25806267
ITABLE_DOM_LONG = "lftipr"
ITABLE_DOM_SHORT = "tr"
GHST_COLOR = 'magenta'
DEFAULT_COLOR = 'royalBlue'
FORGE_ALLOY_COST = { 'common': 100, 'uncommon': 300, 'rare': 1300, 'legendary': 5300, 'mythical': 25000, 'godlike': 130000 }
SMELT_ALLOY_RECEIVED = { 'common': 90, 'uncommon': 270, 'rare': 1170, 'legendary': 4770, 'mythical': 22500, 'godlike': 117000 }