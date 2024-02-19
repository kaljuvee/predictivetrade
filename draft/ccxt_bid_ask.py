import ccxt
import time
from datetime import datetime
import pandas as pd
import argparse
import db_util
import exchange_util

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


def main(exchange_id='bitstamp'):
    #symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD', 'SOL/USD', 'LINK/USD', 'AVAX/USD', 'ADA/USD', 'MATIC/USD', 'SUI/USD', 'XLM/USD', 'GALA/USD']
    #limit = 20
    file_name = 'symbol_exchange.csv'
    symbols = exchange_util.get_symbols_from_csv(exchange_id, file_name)
    #symbols = exchange_util.get_symbol_list(exchange_id)

    while True:
        new_data = download(exchange_id, symbols)
        # Convert to DataFrame
        df = pd.DataFrame(new_data, columns=['symbol', 'timestamp', 'bid', 'ask', 'exchange'])

        try:
            # Attempt to write the fetched data to the database
            db_util.write_bid_ask(df)
            print('Successfully wrote to database')
        except Exception as e:
            # Handle database-related exceptions
            print(f'Failed to write to database: {e}')

        time.sleep(60)  # Sleep for 60 seconds before the next fetch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download order book data.')
    parser.add_argument('-e', '--exchange', default='bitstamp', help='Exchange ID (default: bitstamp)')
    args = parser.parse_args()

    main(args.exchange)
