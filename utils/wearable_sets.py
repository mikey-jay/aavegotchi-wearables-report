import ast
import pandas as pd
from utils.subgraph import get_core_matic_query, get_subgraph_result_df
from shared import UPDATE_TIME_HASH, TRAIT_NAMES, USE_CACHE, RARITY_SCORE_MODIFIERS

RARITY_SCORE_MODIFIER_NAMES = ["rarityScoreModifier"] + TRAIT_NAMES[0:4]

def import_wearable_sets_csv(csv_filename):
    wearable_sets_df = pd.read_csv(csv_filename, index_col=0)
    for column_name in ['traitBonuses', 'wearableIds', 'allowedCollaterals']:
        wearable_sets_df[column_name] = wearable_sets_df[column_name].apply(ast.literal_eval)
    return wearable_sets_df

def get_wearable_sets_df(wearable_types_df):
    # wearable sets have many issues in subgraph, keeping it in a CSV for now - this will need to be updated manually

    wearable_sets_df = import_wearable_sets_csv('data/wearable_sets.csv')

    # split trait modifiers into individual columns
    wearable_sets_df[RARITY_SCORE_MODIFIER_NAMES] = wearable_sets_df['traitBonuses'].apply(pd.Series)
    wearable_sets_df.drop(columns=['traitBonuses'], inplace=True)
    wearable_sets_df.reset_index(drop=True, inplace=True)
    wearable_sets_df.index.set_names(['set_index'], inplace=True)
    return wearable_sets_df

def filter_wearable_sets_by_rarity_range(wearable_sets_df, wearable_types_df, max_range_rule = {1: 0, 2: 1, 5: 2, 10: 3, 20: 2, 50: 1}):
    # exclude sets that don't fit rarity range requirements
    set_wearable_rarity_tier_range = get_set_wearable_rarity_tier_range(wearable_sets_df, wearable_types_df)
    set_wearable_max_rarity = get_set_wearable_max_rarity(wearable_sets_df, wearable_types_df)
    within_max_rarity_range_filter = set_wearable_rarity_tier_range <= set_wearable_max_rarity.apply(lambda rarity: max_range_rule[rarity])
    return wearable_sets_df[within_max_rarity_range_filter]

def get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=['name'], wearable_fields=['name']):
    wearable_set_membership_df = wearable_sets_df.reset_index().explode('wearableIds')[['set_index', 'wearableIds']].rename(columns={'wearableIds': 'wearable_id'}).reset_index(drop=True)
    wearable_set_membership_df = wearable_set_membership_df.merge(wearable_sets_df[set_fields], left_on='set_index', right_index=True, how='left', suffixes=('_set', '_wearable'))
    wearable_set_membership_df = wearable_set_membership_df.merge(wearable_types_df[wearable_fields], left_on='wearable_id', right_index=True, how='left', suffixes=('_set', '_wearable'))
    wearable_set_membership_df.set_index(['set_index', 'wearable_id'], inplace=True)
    return wearable_set_membership_df

def get_set_wearables_count(wearable_sets_df):
    return wearable_sets_df['wearableIds'].apply(lambda x: len(x))

def get_set_collateral_count(wearable_sets_df):
    return wearable_sets_df['allowedCollaterals'].apply(lambda x: len(x))

def get_set_trait_count(wearable_sets_df):
    traits_modified_by_set = wearable_sets_df[RARITY_SCORE_MODIFIER_NAMES[1:]] != 0
    return traits_modified_by_set.sum(axis=1)

def get_set_with_wearables_trait_count(wearable_sets_df, wearable_types_df):
    set_wearable_effects_traits_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=TRAIT_NAMES[0:4]).abs().groupby(level="set_index").sum() > 0
    set_traits_abs_df = wearable_sets_df[TRAIT_NAMES[0:4]].abs() > 0
    set_with_wearables_trait_count = (set_wearable_effects_traits_df | set_traits_abs_df).sum(axis=1)
    return set_with_wearables_trait_count

def get_set_max_quantity(wearable_sets_df, wearable_types_df):
    set_wearable_quantities_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, wearable_fields=['maxQuantity'])
    set_wearable_quantities = set_wearable_quantities_df['maxQuantity'].groupby(level='set_index').min()
    return set_wearable_quantities

def get_set_wearable_rarity_stddev(wearable_sets_df, wearable_types_df):
    set_wearable_rarities_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=['rarityScoreModifier'])
    set_wearable_rarity_stddev = set_wearable_rarities_df['rarityScoreModifier'].groupby(level='set_index').std()
    return set_wearable_rarity_stddev

def get_set_wearable_rarity_range(wearable_sets_df, wearable_types_df):
    set_wearable_rarities_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=['rarityScoreModifier'])
    set_wearable_rarity_group = set_wearable_rarities_df['rarityScoreModifier'].groupby(level='set_index')
    set_wearable_rarity_range = set_wearable_rarity_group.max() - set_wearable_rarity_group.min()
    return set_wearable_rarity_range

def get_set_wearable_max_rarity(wearable_sets_df, wearable_types_df):
    set_wearable_rarities_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=['rarityScoreModifier'])
    set_wearable_max_rarity = set_wearable_rarities_df['rarityScoreModifier'].groupby(level='set_index').max()
    return set_wearable_max_rarity

def get_set_wearable_rarity_tier_range(wearable_sets_df, wearable_types_df):
    set_wearable_rarities_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=['rarityScoreModifier'])
    set_wearable_rarity_tier_group = set_wearable_rarities_df['rarityScoreModifier'].apply(lambda rarity: list(RARITY_SCORE_MODIFIERS.keys()).index(rarity)).groupby(level='set_index')
    set_wearable_rarity_tier_range = set_wearable_rarity_tier_group.max() - set_wearable_rarity_tier_group.min()
    return set_wearable_rarity_tier_range

def get_equipped_sets(wearable_sets_df, equipped_wearable_ids):
    is_equipped = wearable_sets_df.apply(lambda row: all(wearable_ids in equipped_wearable_ids for wearable_ids in row['wearableIds']), axis=1)
    return wearable_sets_df[is_equipped]

def get_set_equip_counts(wearable_sets_df, equippedWearablesSeries):
    rf_set_equip_counts = equippedWearablesSeries.apply(lambda equipped_wearable_ids: get_equipped_sets(wearable_sets_df, equipped_wearable_ids).index.tolist()).explode().value_counts()
    return rf_set_equip_counts

def get_set_with_wearables_brs_effect(wearable_sets_df, wearable_types_df):
    set_wearable_modifiers_df = get_wearable_set_membership_df(wearable_sets_df, wearable_types_df, set_fields=[], wearable_fields=RARITY_SCORE_MODIFIER_NAMES)
    set_trait_modifiers_df = wearable_sets_df[RARITY_SCORE_MODIFIER_NAMES]
    set_with_wearables_trait_modifiers_df = set_wearable_modifiers_df.groupby(level='set_index').sum() + set_trait_modifiers_df
    set_with_wearables_combined_brs_effect = set_with_wearables_trait_modifiers_df.abs().sum(axis=1)
    return set_with_wearables_combined_brs_effect