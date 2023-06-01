import pandas as pd
from utils.wearable_traits import get_trait_permutations, make_trait_permutation_list
from shared import RARITY_SCORE_MODIFIERS

def fits_gotchi_traits(gotchi_traits, wearable_traits):
    for trait in wearable_traits:
        if trait not in gotchi_traits:
            return False
    return True

def filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df):
    wearable_trait_modifiers = wearable_types_df.apply(make_trait_permutation_list, axis=1)
    fits = wearable_trait_modifiers.apply(lambda wearable_traits: fits_gotchi_traits(gotchi_traits, wearable_traits))
    return wearable_types_df[fits.tolist()]

def get_fit_count(gotchi_traits, wearable_types_df):
    wearable_types_fits_df = filter_wearable_types_df_by_gotchi_fit(gotchi_traits, wearable_types_df)
    return len(wearable_types_fits_df)

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
                
            rarity_sort = list(RARITY_SCORE_MODIFIERS.values()).index(rarity)
            
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

def calculate_change_in_fit_count_stddev(gotchi_wearable_fit_counts_df, trait_modifiers_to_add):
    gotchi_wearable_fit_counts_comparison = gotchi_wearable_fit_counts_df.copy()
    gotchi_wearable_fit_counts_comparison['added_wearable_fits'] = gotchi_wearable_fit_counts_comparison.apply(lambda row: fits_gotchi_traits(row['gotchi_traits'], trait_modifiers_to_add), axis=1)
    gotchi_wearable_fit_counts_comparison['fit_count_after_addition'] = gotchi_wearable_fit_counts_comparison['fit_count'] + gotchi_wearable_fit_counts_comparison['added_wearable_fits']
    standard_deviation_before, standard_deviation_after = gotchi_wearable_fit_counts_comparison[['fit_count', 'fit_count_after_addition']].std()
    change_in_standard_deviation = standard_deviation_after - standard_deviation_before
    return change_in_standard_deviation

def get_all_trait_permutations():
    all_trait_permutations = []
    for trait_count in range(1,4):
        all_trait_permutations.extend(get_trait_permutations(trait_count))
    return all_trait_permutations

def get_changes_to_fit_count_stddev_df(wearable_types_df):
    all_trait_permutations = get_all_trait_permutations()
    gotchi_wearable_fit_counts_df = get_all_gotchi_wearable_fit_counts_df(wearable_types_df)
    trait_modifier_changes_to_fit_count_stddev = []
    for trait_modifiers_to_add in all_trait_permutations:
        change_in_fit_count_stddev = calculate_change_in_fit_count_stddev(gotchi_wearable_fit_counts_df, trait_modifiers_to_add)
        trait_modifier_changes_to_fit_count_stddev.append([trait_modifiers_to_add, len(trait_modifiers_to_add), change_in_fit_count_stddev])

    return pd.DataFrame(trait_modifier_changes_to_fit_count_stddev, columns=['trait_modifiers_to_add', 'trait_modifier_count', 'change_in_fit_count_stddev'])

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
