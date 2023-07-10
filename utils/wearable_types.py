import utils.database as db
import datetime
import pandas as pd
import numpy as np
from utils.subgraph import get_core_matic_query, get_subgraph_result_df
from utils.import_item_types_csv import import_item_types_csv
from utils.config import ITEM_TYPE_CATEGORY_WEARABLE, UPDATE_TIME_HASH, EXCLUDE_WEARABLE_IDS, USE_CACHE, SLOT_POSITION_NAMES, TRAIT_NAMES, RARITY_SCORE_MODIFIERS, UPDATE_TIME

WEARABLE_TYPES_TABLE_NAME = 'wearable_types'

def get_wearable_types_from_database() -> pd.DataFrame:
    return db.get_df_from_database(WEARABLE_TYPES_TABLE_NAME).set_index('id')

def store_wearable_types_to_database(df: pd.DataFrame):
    return db.store_df_to_database(WEARABLE_TYPES_TABLE_NAME, df)

def get_wearable_types_df():
    if datetime.datetime.fromtimestamp(UPDATE_TIME) > db.get_table_modified_time(WEARABLE_TYPES_TABLE_NAME):
        wearable_types_df = get_wearable_types_from_subgraph()
        store_wearable_types_to_database(wearable_types_df)
    else:
        wearable_types_df = get_wearable_types_from_database()    
    return wearable_types_df

def get_wearable_types_from_subgraph():
    
    wearables_query = get_core_matic_query(
    { 'itemTypes': {
        'params': { 'where': { 'category': ITEM_TYPE_CATEGORY_WEARABLE, 'id_not': UPDATE_TIME_HASH, 'id_not_in': list(map(str, EXCLUDE_WEARABLE_IDS)), 'canBeTransferred': True } },
        'fields': ["id", "name", "traitModifiers", "slotPositions", "maxQuantity", "rarityScoreModifier"] }}
    )

    wearables_result = wearables_query.execute(USE_CACHE)

    # temporarily patch the results to include the latest wearable types - due to bug with core matic subgraph
    # uncomment these two lines and delete the patch below when the core matic subgraph is fixed to include forge wearables

    # wearable_types_df = get_subgraph_result_df(wearables_result)
    # wearable_types_df.set_index(wearable_types_df.index.astype(np.int64), inplace=True)

    wearable_types_from_subgraph_df = get_subgraph_result_df(wearables_result)
    wearable_types_from_subgraph_df.set_index(wearable_types_from_subgraph_df.index.astype(np.int64), inplace=True)
    forge_wearable_types_df = import_item_types_csv('data/forge_wearable_types.csv')
    missing_wearable_types = forge_wearable_types_df[~forge_wearable_types_df.index.isin(wearable_types_from_subgraph_df.index)]
    wearable_types_df = pd.concat([wearable_types_from_subgraph_df, missing_wearable_types])
    
    # end of patch

    wearable_types_df.sort_index(inplace=True)
    item_types_int_fields = ['maxQuantity', 'rarityScoreModifier']
    wearable_types_df[item_types_int_fields] = wearable_types_df[item_types_int_fields].astype(np.int64)

    # trait modifiers
    append = lambda s2: lambda s1: str(s1) + str(s2)
    traitEffectColumns = list(map(append(' Effect'), TRAIT_NAMES))
    getTraitEffect = lambda s: pd.Series(s).apply(lambda modifier: '+' if modifier > 0 else '-' if modifier < 0 else '')
    wearable_types_df[TRAIT_NAMES] = wearable_types_df['traitModifiers'].apply(pd.Series)
    wearable_types_df[traitEffectColumns] = wearable_types_df['traitModifiers'].apply(getTraitEffect)

    for trait in TRAIT_NAMES:
        wearable_types_df[f'{trait} Supply'] = wearable_types_df[trait] * wearable_types_df['maxQuantity']

    wearable_types_df['bestFitRarityScoreModifier'] =  wearable_types_df[["rarityScoreModifier"] + TRAIT_NAMES[0:4]].abs().sum(axis=1)
    wearable_types_df['traitModifierCount'] = wearable_types_df['traitModifiers'].apply(lambda row: len(list(filter(lambda x: x != 0, row))))

    wearable_types_df.drop(['traitModifiers', 'EYS', 'EYC', 'EYS Effect', 'EYC Effect', 'EYS Supply', 'EYC Supply'], axis=1, inplace=True)

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