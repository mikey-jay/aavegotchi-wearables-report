def get_wearables_market_cap_df(circulating_supply_df, purchases_df):
    last_price = purchases_df.groupby('erc1155TypeId').last(1)['price'].rename('lastPrice')
    market_cap_df = circulating_supply_df.join(last_price).fillna(0)
    market_cap_df['marketCap'] = market_cap_df['lastPrice'] * market_cap_df['circulating_supply']
    return market_cap_df