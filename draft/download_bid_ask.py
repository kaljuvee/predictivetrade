import ccxt
import time
from datetime import datetime
import pandas as pd
import argparse
from util import db_util, exchange_util

exchanges_symbols = {
    'bitstamp': ['BTC/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD', 'SOL/USD', 'LINK/USD', 'AVAX/USD', 'ADA/USD', 'MATIC/USD', 'SUI/USD', 'XLM/USD', 'GALA/USD'],
    'kraken': ['BTC/USD', 'SOL/USD', 'ETH/USD', 'AVAX/USD', 'INJ/USD', 'SOL/USDT', 'TIA/USD', 'MATIC/USD', 'LINK/USD', 'ICP/USD', 'SEI/USD', 'ADA/USD', 'DOGE/USD'],
    'poloniex': ['BTC/USDT', 'ETH/USDT', 'HTX/USDT', 'LINK/USDT', 'SUN/USDT', 'SAND/USDT', 'WIN/USDT', 'NFT/USDT', 'JST/USDT', 'ADA/USDT', 'DOGE/USDT', 'EOS/USDT', 'MATIC/USDT', 'SHIB/USDT', 'NAKA/USDT', 'IMX/USDT', 'BTT/USDT', 'BCH/USDT', 'LTC/USDT', 'ARB/USDT']
}

def download(exchange_id, symbols):
    historical_data = []

    # Dynamically load the exchange class based on the exchange_id
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class()

    for symbol in symbols:
        try:
            print(f"Starting download for {symbol} on {exchange_id}")
            order_book = exchange.fetch_order_book(symbol)
            top_bid = order_book['bids'][0][0] if order_book['bids'] else None
            top_ask = order_book['asks'][0][0] if order_book['asks'] else None
            
            # Convert timestamp from milliseconds to datetime object and then to ISO 8601 format
            timestamp_ms = exchange.milliseconds()
            timestamp_iso = datetime.utcfromtimestamp(timestamp_ms / 1000.0).isoformat()
            
            historical_data.append([symbol, timestamp_iso, top_bid, top_ask, exchange_id])
            print(f"Completed download for {symbol} on {exchange_id}")
        except Exception as e:
            print(f"Error fetching data for {symbol} on {exchange_id}: {e}")

    return historical_data


def main():
    while True:
        for exchange_id, symbols in exchanges_symbols.items():
            print('getting data for: ', exchange_id)
            new_data = download(exchange_id, symbols)
            # Convert to DataFrame
            df = pd.DataFrame(new_data, columns=['symbol', 'timestamp', 'bid', 'ask', 'exchange'])

            try:
                # Attempt to write the fetched data to the database
                db_util.write_bid_ask(df)
                print(f'Successfully wrote {exchange_id} data to database')
            except Exception as e:
                # Handle database-related exceptions
                print(f'Failed to write {exchange_id} data to database: {e}')
        
        # Sleep for 60 seconds after processing all exchanges, before the next fetch cycle begins
        print('Waiting 60 seconds before the next update...')
        time.sleep(60)

if __name__ == '__main__':
    main()
