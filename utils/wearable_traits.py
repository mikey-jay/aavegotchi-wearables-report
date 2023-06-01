from utils.concatenation_combinations import get_n_length_concatenation_combinations
import pandas as pd
import numpy as np

def get_trait_permutations(num_traits=4):
    traits = ['NRG', 'AGG', 'SPK', 'BRN']
    polarities = ['+', '-']
    return get_n_length_concatenation_combinations(traits, polarities, num_traits)

def make_trait_permutation_list(row, traits=['NRG', 'AGG', 'SPK', 'BRN']):
    trait_permutation = []
    for trait in traits:
        if row[trait] > 0:
            trait_permutation.append(f'{trait}+')
        elif row[trait] < 0:
            trait_permutation.append(f'{trait}-')
    return trait_permutation

def make_trait_permutation_string(row, traits=['NRG', 'AGG', 'SPK', 'BRN']):
    return ', '.join(make_trait_permutation_list(row, traits))

def get_trait_modifier_count_df(source_df):
    df = source_df.copy()
    df['traitPermutation'] = df.apply(make_trait_permutation_string, axis=1)
    df['count'] = 1
    df = df[['traitPermutation', 'count']].groupby(['traitPermutation']).count()
    return df

def get_trait_distribution_df(source_df, num_traits=2, traits=['NRG', 'AGG', 'SPK', 'BRN']):
    df = get_trait_modifier_count_df(source_df)
    trait_distribution_columns = []
    for trait in traits:
        trait_distribution_columns.extend([f'{trait}+', f'{trait}-'])
    trait_permutations = get_trait_permutations(num_traits)
    trait_distribution_data = {}
    for traits_permutation in trait_permutations:
        trait_permutation_string = ', '.join(traits_permutation)
        primary_trait = traits_permutation[0]
        if primary_trait not in trait_distribution_data:
            trait_distribution_data[primary_trait] = {}
        paired_traits = ', '.join(traits_permutation[1:])
        if paired_traits not in trait_distribution_data[primary_trait]:
            trait_distribution_data[primary_trait][paired_traits] = 0
        if trait_permutation_string in df.index:
            trait_distribution_data[primary_trait][paired_traits] += df.loc[trait_permutation_string]['count']
        else:
            trait_distribution_data[primary_trait][paired_traits] = 0
    return pd.DataFrame(trait_distribution_data)
