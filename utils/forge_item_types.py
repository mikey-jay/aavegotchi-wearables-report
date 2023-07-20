import utils.database as db
import datetime
import pandas as pd
import numpy as np
from utils.config import (
    UPDATE_TIME_HASH,
    USE_CACHE,
    SLOT_POSITION_NAMES,
    TRAIT_NAMES,
    UPDATE_TIME,
)

def get_forge_item_types_df(wearable_types_df):
    forge_item_types_df = pd.read_csv('data/forge_item_types.csv', index_col=0, dtype={'id': np.int64}).fillna("")
    forge_item_types_df['name'] = forge_item_types_df[['rarity', 'slot', 'category_name']].apply(lambda row: " ".join(row), axis=1)

    schematic_item_types_df = wearable_types_df[['name', 'slotNames', 'rarity']].copy().rename(columns={'slotNames': 'slot'})
    schematic_item_types_df['name'] = schematic_item_types_df['name'].apply(lambda name: str.lower(name) + " schematic")
    schematic_item_types_df['category_name'] = "schematic"

    return pd.concat([forge_item_types_df, schematic_item_types_df]).sort_index()
