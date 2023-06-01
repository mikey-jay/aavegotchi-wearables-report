import ast
import pandas as pd

def import_item_types_csv(csv_filename):
    item_types_df = pd.read_csv(csv_filename, index_col=0, dtype={'maxQuantity': str})
    item_types_df['traitModifiers'] = item_types_df['traitModifiers'].apply(ast.literal_eval)
    item_types_df['slotPositions'] = item_types_df['slotPositions'].apply(ast.literal_eval)
    return item_types_df