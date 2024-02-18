import pandas as pd
import ccxt

def get_symbols_no_eur(exchange_id):
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        all_symbols = exchange.load_markets().keys()
        # Filter out symbols that are paired with EUR
        filtered_symbols = [symbol for symbol in all_symbols if not symbol.endswith('/EUR')]
        return filtered_symbols, None  # Return symbols and no error
    except Exception as e:
        return [], str(e)  # Return empty list and error message

def get_prices(selected_symbols, timeframe):
    exchange = ccxt.bitstamp()
    all_data = pd.DataFrame()

    for symbol in selected_symbols:
        try:
            limit = 1440  # Maximum number of data points
            since = exchange.milliseconds() - 86400000  # Last 24 hours
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data['symbol'] = symbol
            all_data = pd.concat([all_data, data])
        except Exception as e:
            st.error(f"Error fetching data for {symbol}: {e}")

    return all_data

def get_top_coins_by_volume(exchange_id, limit=15):
    try:
        # Initialize the exchange
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()

        # Load markets
        exchange.load_markets()

        # Fetch ticker information for all symbols
        tickers = exchange.fetch_tickers()

        # Specify the base currencies you want to exclude
        excluded_base_currencies = ['GBP', 'EUR', 'CHF']

        # Filter out tickers that have the excluded base currencies
        filtered_tickers = {symbol: ticker for symbol, ticker in tickers.items()
                            if not any(base_currency in symbol for base_currency in excluded_base_currencies)}

        # Sort the filtered tickers by volume and get the top 'limit' tickers
        sorted_tickers = sorted(filtered_tickers.values(), key=lambda x: x['quoteVolume'], reverse=True)[:limit]

        # Create a list of top coins with their volumes
        top_coins = [ticker['symbol'] for ticker in sorted_tickers]
        return top_coins
    except Exception as e:
        return str(e)
