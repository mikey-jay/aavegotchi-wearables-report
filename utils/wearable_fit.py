import pandas as pd
from utils.wearable_traits import get_trait_permutations, make_trait_permutation_list
from shared import RARITY_SCORE_MODIFIERS, get_rarity_sort_value

def fits_gotchi_traits(gotchi_traits, wearable_traits):
    for trait in wearable_traits:
        if trait not in gotchi_traits:
            return False
    return True

def get_opposite_trait(trait):
    trait_name = trait[:3]
    trait_polarity = trait[-1]
    if trait_polarity == '+':
        return trait_name + '-'
    elif trait_polarity == '-':
        return trait_name + '+'

def call_fn_by_rarity(fn, wearable_types_df, **args):
    results = pd.DataFrame()
    for rarity in wearable_types_df['rarity'].unique():
        results_for_rarity = fn(wearable_types_df[wearable_types_df['rarity'] == rarity], **args)
        results_for_rarity['rarity'] = rarity
        results_for_rarity['rarity_sort'] = get_rarity_sort_value(rarity)
        results = pd.concat([results, results_for_rarity])
    return results

def get_all_gotchi_set_wearable_fit_counts_by_rarity_df(wearable_types_df, wearable_sets_df):
    return call_fn_by_rarity(get_all_gotchi_set_wearable_fit_counts_df, wearable_types_df, wearable_sets_df=wearable_sets_df)

def get_changes_to_set_wearable_fit_count_by_rarity_stddev_df(wearable_types_df, wearable_sets_df):
    return call_fn_by_rarity(get_changes_to_set_wearable_fit_count_stddev_df, wearable_types_df, wearable_sets_df=wearable_sets_df)

def filter_wearable_sets_df_by_gotchi_fit(gotchi_traits, wearable_sets_df, wearable_types_df):
    wearable_types_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df)
    wearable_sets_bonus_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_sets_df)
    wearable_set_fits_filter = wearable_sets_bonus_fits_df['wearableIds'].apply(lambda wearable_ids: all([wearable_id in wearable_types_fits_df.index for wearable_id in wearable_ids]))
    return wearable_sets_bonus_fits_df[wearable_set_fits_filter.tolist()]

def filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df):
    wearable_trait_modifiers = wearable_types_df.apply(make_trait_permutation_list, axis=1)
    fits = wearable_trait_modifiers.apply(lambda wearable_traits: fits_gotchi_traits(gotchi_traits, wearable_traits))
    return wearable_types_df[fits.tolist()]

def get_fit_count(gotchi_traits, wearable_types_df):
    wearable_types_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df)
    return len(wearable_types_fits_df)

def get_set_fit_count(gotchi_traits, wearable_sets_df, wearable_types_df):
    wearable_sets_fits_df = filter_wearable_sets_df_by_gotchi_fit(gotchi_traits, wearable_sets_df, wearable_types_df)
    return len(wearable_sets_fits_df)

# count the number of unique wearables that fit a gotchi and a fitting set for that gotchi
def get_set_wearable_fit_count(gotchi_traits, wearable_sets_df, wearable_types_df):
    return len(get_set_wearable_fits(gotchi_traits, wearable_sets_df, wearable_types_df))

# get a list of all the unique wearables that fit a gotchi and a fitting set for that gotchi
def get_set_wearable_fits(gotchi_traits, wearable_sets_df, wearable_types_df):
    wearable_sets_fits_df = filter_wearable_sets_df_by_gotchi_fit(gotchi_traits, wearable_sets_df, wearable_types_df)
    if len(wearable_sets_fits_df) == 0:
        return pd.DataFrame(columns=wearable_types_df.columns) 
    fits_ids = wearable_sets_fits_df.explode('wearableIds')['wearableIds'].unique()
    return wearable_types_df[wearable_types_df.index.isin(fits_ids)]

def get_wearable_fits_not_in_sets(gotchi_traits, wearable_sets_df, wearable_types_df):
    wearable_types_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df)
    set_wearable_fits_df = get_set_wearable_fits(gotchi_traits, wearable_sets_df, wearable_types_df)
    return wearable_types_fits_df[~wearable_types_fits_df.index.isin(set_wearable_fits_df.index)]

def get_all_gotchi_set_wearable_fit_counts_df(wearable_types_df, wearable_sets_df):

    all_gotchi_trait_permutations = get_trait_permutations(num_traits=4)

    gotchi_wearable_set_fit_counts = []

    for gotchi_traits in all_gotchi_trait_permutations:
        wearables_without_set_fit = get_wearable_fits_not_in_sets(gotchi_traits, wearable_sets_df, wearable_types_df)['name'].values
        gotchi_wearable_set_fit_counts.append([gotchi_traits, get_set_wearable_fit_count(gotchi_traits, wearable_sets_df, wearable_types_df), wearables_without_set_fit])
   

    gotchi_wearable_set_fit_counts_df = pd.DataFrame(gotchi_wearable_set_fit_counts, columns=['gotchi_traits', 'fit_count', 'wearables_without_set_fit'])
    gotchi_wearable_set_fit_counts_df.sort_values(by=['fit_count'], ascending=False, inplace=True)

    return gotchi_wearable_set_fit_counts_df

def get_all_gotchi_set_fit_counts_df(wearable_types_df, wearable_sets_df):

    all_gotchi_trait_permutations = get_trait_permutations(num_traits=4)

    gotchi_wearable_set_fit_counts = []

    for gotchi_traits in all_gotchi_trait_permutations:
        wearables_without_set_fit = get_wearable_fits_not_in_sets(gotchi_traits, wearable_sets_df, wearable_types_df)['name'].values
        gotchi_wearable_set_fit_counts.append([gotchi_traits, get_set_fit_count(gotchi_traits, wearable_sets_df, wearable_types_df), wearables_without_set_fit])

    gotchi_wearable_set_fit_counts_df = pd.DataFrame(gotchi_wearable_set_fit_counts, columns=['gotchi_traits', 'fit_count', 'wearables_without_set_fit'])
    gotchi_wearable_set_fit_counts_df.sort_values(by=['fit_count'], ascending=False, inplace=True)

    return gotchi_wearable_set_fit_counts_df

def get_all_gotchi_wearable_fit_counts_df(wearable_types_df):

    all_gotchi_trait_permutations = get_trait_permutations(num_traits=4)

    gotchi_wearable_fit_counts = []

    for gotchi_traits in all_gotchi_trait_permutations:
        gotchi_wearable_fit_counts.append([gotchi_traits, get_fit_count(gotchi_traits, wearable_types_df)])

    gotchi_wearable_fit_counts_df = pd.DataFrame(gotchi_wearable_fit_counts, columns=['gotchi_traits', 'fit_count'])
    gotchi_wearable_fit_counts_df.sort_values(by=['fit_count'], ascending=False, inplace=True)

    return gotchi_wearable_fit_counts_df

def add_wearable_to_fit_counts_df(gotchi_wearable_fit_counts_df, trait_modifiers_to_add):
    fit_counts_after_addition_df = gotchi_wearable_fit_counts_df.copy()
    fits = gotchi_wearable_fit_counts_df.apply(lambda row: fits_gotchi_traits(row['gotchi_traits'], trait_modifiers_to_add), axis=1)
    fit_counts_after_addition_df['fit_count'] = fit_counts_after_addition_df['fit_count'] + fits
    return fit_counts_after_addition_df

def get_all_gotchi_wearable_fit_counts_by_slot_rarity_df(wearable_types_df):

    all_gotchi_trait_permutations = get_trait_permutations(num_traits=4)
    fit_counts_by_slot_rarity = []
    
    for gotchi_traits in all_gotchi_trait_permutations:

        for rarity in wearable_types_df['rarity'].unique():
                
            rarity_sort = get_rarity_sort_value(rarity)
            
            for slot in wearable_types_df['slotNames'].unique():
        
                wearables_filtered_by_rarity_slot = wearable_types_df[(wearable_types_df['rarity'] == rarity) & (wearable_types_df['slotNames'] == slot)]
                rarity_slot_wearable_count = len(wearables_filtered_by_rarity_slot)

                if rarity_slot_wearable_count == 0:
                    rarity_slot_fit_count = 0
                    rarity_slot_fit_proportion = pd.NA
                else:
                    wearable_types_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearables_filtered_by_rarity_slot)
                    rarity_slot_fit_count = len(wearable_types_fits_df)
                    rarity_slot_fit_proportion = rarity_slot_fit_count / rarity_slot_wearable_count

                fit_counts_by_slot_rarity.append([gotchi_traits, rarity, rarity_sort, slot, rarity_slot_wearable_count, rarity_slot_fit_count, rarity_slot_fit_proportion])

    gotchi_wearable_fit_counts_df = pd.DataFrame(fit_counts_by_slot_rarity, columns=['gotchi_traits', 'rarity', 'rarity_sort', 'slot', 'rarity_slot_wearable_count', 'rarity_slot_fit_count', 'rarity_slot_fit_proportion'])
    gotchi_wearable_fit_counts_df.sort_values(by=['rarity_sort', 'slot', 'rarity_slot_fit_proportion'], ascending=True, inplace=True)

    return gotchi_wearable_fit_counts_df

def calculate_change_in_rarity_slot_fit_count_stddev(gotchi_wearable_fit_counts_df, rarity_to_add, slot_to_add, trait_modifiers_to_add):
    gotchi_wearable_fit_counts_comparison = gotchi_wearable_fit_counts_df[(gotchi_wearable_fit_counts_df['rarity'] == rarity_to_add) & (gotchi_wearable_fit_counts_df['slot'] == slot_to_add)].copy()
    gotchi_wearable_fit_counts_comparison['added_wearable_fits'] = gotchi_wearable_fit_counts_comparison.apply(lambda row: fits_gotchi_traits(row['gotchi_traits'], trait_modifiers_to_add), axis=1)
    gotchi_wearable_fit_counts_comparison['rarity_slot_fit_count_after_addition'] = gotchi_wearable_fit_counts_comparison['rarity_slot_fit_count'] + gotchi_wearable_fit_counts_comparison['added_wearable_fits']
    standard_deviation_before, standard_deviation_after = gotchi_wearable_fit_counts_comparison[['rarity_slot_fit_count', 'rarity_slot_fit_count_after_addition']].std()
    change_in_standard_deviation = standard_deviation_after - standard_deviation_before
    return change_in_standard_deviation

def calculate_change_in_fit_count_stddev(gotchi_wearable_fit_counts_df, trait_modifiers_to_add, num_pieces_to_add = 1):
    gotchi_wearable_fit_counts_comparison = gotchi_wearable_fit_counts_df.copy()
    gotchi_wearable_fit_counts_comparison['added_wearable_fits'] = gotchi_wearable_fit_counts_comparison.apply(lambda row: fits_gotchi_traits(row['gotchi_traits'], trait_modifiers_to_add), axis=1)
    gotchi_wearable_fit_counts_comparison['fit_count_after_addition'] = gotchi_wearable_fit_counts_comparison['fit_count'] + (gotchi_wearable_fit_counts_comparison['added_wearable_fits'] * num_pieces_to_add)
    standard_deviation_before, standard_deviation_after = gotchi_wearable_fit_counts_comparison[['fit_count', 'fit_count_after_addition']].std()
    change_in_standard_deviation = standard_deviation_after - standard_deviation_before
    return change_in_standard_deviation

def calculate_change_in_fit_count_nonzero(gotchi_wearable_fit_counts_df, trait_modifiers_to_add, num_pieces_to_add = 1):
    gotchi_wearable_fit_counts_comparison = gotchi_wearable_fit_counts_df.copy()
    gotchi_wearable_fit_counts_comparison['added_wearable_fits'] = gotchi_wearable_fit_counts_comparison.apply(lambda row: fits_gotchi_traits(row['gotchi_traits'], trait_modifiers_to_add), axis=1)
    gotchi_wearable_fit_counts_comparison['fit_count_after_addition'] = gotchi_wearable_fit_counts_comparison['fit_count'] + (gotchi_wearable_fit_counts_comparison['added_wearable_fits'] * num_pieces_to_add)
    nonzero_fit_count_before = (gotchi_wearable_fit_counts_comparison['fit_count'] > 0).sum()
    nonzero_fit_count_after = (gotchi_wearable_fit_counts_comparison['fit_count_after_addition'] > 0).sum()
    change_in_nonzero_fit_count = nonzero_fit_count_after - nonzero_fit_count_before
    return change_in_nonzero_fit_count

def get_all_trait_permutations(max_trait_count=3):
    all_trait_permutations = []
    for trait_count in range(1,max_trait_count+1):
        all_trait_permutations.extend(get_trait_permutations(trait_count))
    return all_trait_permutations

def get_changes_to_wearable_fit_count_stddev_df(wearable_types_df):
    gotchi_wearable_fit_counts_df = get_all_gotchi_wearable_fit_counts_df(wearable_types_df)
    return get_change_to_fit_count_stddev_df(gotchi_wearable_fit_counts_df)

def get_changes_to_wearable_fit_count_nonzero_df(wearable_types_df):
    gotchi_wearable_fit_counts_df = get_all_gotchi_wearable_fit_counts_df(wearable_types_df)
    return get_change_in_fit_count_nonzero_df(gotchi_wearable_fit_counts_df)

def get_changes_to_set_fit_count_stddev_df(wearable_types_df, wearable_sets_df):
    gotchi_wearable_set_fit_counts_df = get_all_gotchi_set_fit_counts_df(wearable_types_df, wearable_sets_df)
    return get_change_to_fit_count_stddev_df(gotchi_wearable_set_fit_counts_df)

def get_changes_to_set_wearable_fit_count_stddev_df(wearable_types_df, wearable_sets_df, num_pieces_in_set=3):
    gotchi_set_wearable_fit_counts_df = get_all_gotchi_set_wearable_fit_counts_df(wearable_types_df, wearable_sets_df)
    return get_change_to_fit_count_stddev_df(gotchi_set_wearable_fit_counts_df, num_pieces_to_add=num_pieces_in_set, max_trait_count=4)

def get_change_to_fit_count_stddev_df(fit_count_df, num_pieces_to_add=1, max_trait_count=3):
    all_trait_permutations = get_all_trait_permutations(max_trait_count=max_trait_count)
    trait_modifier_changes_to_fit_count_stddev = []
    for trait_modifiers_to_add in all_trait_permutations:
        change_in_fit_count_stddev = calculate_change_in_fit_count_stddev(fit_count_df, trait_modifiers_to_add, num_pieces_to_add=num_pieces_to_add)
        trait_modifier_changes_to_fit_count_stddev.append([trait_modifiers_to_add, len(trait_modifiers_to_add), change_in_fit_count_stddev])
    return pd.DataFrame(trait_modifier_changes_to_fit_count_stddev, columns=['trait_modifiers_to_add', 'trait_modifier_count', 'change_in_fit_count_stddev'])

def get_change_in_fit_count_nonzero_df(fit_count_df, num_pieces_to_add=1, max_trait_count=3):
    all_trait_permutations = get_all_trait_permutations(max_trait_count=max_trait_count)
    trait_modifier_changes_to_fit_count_nonzero = []
    for trait_modifiers_to_add in all_trait_permutations:
        change_in_fit_count_nonzero = calculate_change_in_fit_count_nonzero(fit_count_df, trait_modifiers_to_add, num_pieces_to_add=num_pieces_to_add)
        trait_modifier_changes_to_fit_count_nonzero.append([trait_modifiers_to_add, len(trait_modifiers_to_add), change_in_fit_count_nonzero])
    return pd.DataFrame(trait_modifier_changes_to_fit_count_nonzero, columns=['trait_modifiers_to_add', 'trait_modifier_count', 'change_in_fit_count_nonzero'])

def get_changes_to_rarity_slot_fit_count_stddev_df(wearable_types_df):
    all_trait_permutations = get_all_trait_permutations()
    gotchi_wearable_fit_counts_slot_rarity_df = get_all_gotchi_wearable_fit_counts_by_slot_rarity_df(wearable_types_df)
    trait_modifier_changes_to_rarity_slot_fit_count_stddev = []
    max_trait_modifiers_length_by_rarity = [1,2,3,3,3,3] # don't include trait modifiers longer than the desired max for the rarity
    for rarity in RARITY_SCORE_MODIFIERS.values():
        rarity_sort = list(RARITY_SCORE_MODIFIERS.values()).index(rarity)
        for slot in wearable_types_df['slotNames'].unique():
            for trait_modifiers_to_add in all_trait_permutations:
                if len(trait_modifiers_to_add) <= max_trait_modifiers_length_by_rarity[rarity_sort]:
                    change_in_rarity_slot_fit_count_stddev = calculate_change_in_rarity_slot_fit_count_stddev(gotchi_wearable_fit_counts_slot_rarity_df, rarity, slot, trait_modifiers_to_add)
                    trait_modifier_changes_to_rarity_slot_fit_count_stddev.append([rarity, rarity_sort, slot, trait_modifiers_to_add, len(trait_modifiers_to_add), change_in_rarity_slot_fit_count_stddev])

    return pd.DataFrame(trait_modifier_changes_to_rarity_slot_fit_count_stddev, columns=['rarity', 'rarity_sort', 'slot', 'trait_modifiers_to_add', 'trait_modifier_count', 'change_in_rarity_slot_fit_count_stddev'])
