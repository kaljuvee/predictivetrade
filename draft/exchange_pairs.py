import ccxt
import pandas as pd

def get_symbols(exchange_id):
    """Fetch available currency pairs for a given exchange."""
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        exchange.load_markets()
        return list(exchange.symbols)
    except Exception as e:
        print(f"Error fetching data for {exchange_id}: {e}")
        return []

def find_common_pairs(exchanges):
    """Find common currency pairs among exchanges."""
    common_pairs = []
    for i in range(len(exchanges)):
        for j in range(i + 1, len(exchanges)):
            symbols_i = set(get_symbols(exchanges[i]))
            symbols_j = set(get_symbols(exchanges[j]))
            common = symbols_i.intersection(symbols_j)
            for pair in common:
                common_pairs.append({'exchange_pair': f"{exchanges[i]}/{exchanges[j]}", 'currency_pair': pair})
    return common_pairs

def main():
    exchanges = ['bitstamp', 'poloniex', 'kraken', 'binance']
    print('getting pairs for: ', exchanges)
    # Find common currency pairs
    common_pairs = find_common_pairs(exchanges)
    
    # Form a DataFrame
    df = pd.DataFrame(common_pairs)

    # Write to CSV
    df.to_csv('common_currency_pairs.csv', index=False)
    print('CSV file has been written successfully.')

if __name__ == "__main__":
    main()
