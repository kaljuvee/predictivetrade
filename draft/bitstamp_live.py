import ccxt
import time
from datetime import datetime
import pandas as pd
import argparse
import db_util
import exchange_util
import file_util
from scipy.stats import zscore
import math

symbols = ['BTC/USD', 'ETH/USD', 'LTC/USD', 'XRP/USD', 'SOL/USD', 'LINK/USD', 'AVAX/USD', 'ADA/USD', 'MATIC/USD', 'SUI/USD', 'XLM/USD', 'GALA/USD']
exchange_id = 'bitstamp'
timeframe = '1m'
days = 1
stop_loss_limit = 0.1
profit_limit = 0.1
maker_fee = 0.1
position_size = 10000
zthreshold = 1

def get_prices(exchange_id, selected_symbols, timeframe, days=1):
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        
        all_data = pd.DataFrame()
        limit_per_call = 1440  # Assuming this as a common safe limit; adjust based on exchange specifics
        interval_in_milliseconds = 60000  # For 1m timeframe; adjust if using a different timeframe
        total_data_points = limit_per_call * days
        number_of_calls = math.ceil(total_data_points / limit_per_call)
        
        for symbol in selected_symbols:
            symbol_data = pd.DataFrame()
            for i in range(number_of_calls):
                since = exchange.milliseconds() - (86400000 * days) + (i * limit_per_call * interval_in_milliseconds)
                try:
                    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit_per_call)
                    data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
                    data['symbol'] = symbol
                    symbol_data = pd.concat([symbol_data, data], ignore_index=True)
                except Exception as e:
                    print(f"Error fetching data for {symbol} on {exchange_id} at call {i+1}: {e}")
            all_data = pd.concat([all_data, symbol_data], ignore_index=True)
                
        return all_data.sort_values(by='timestamp').reset_index(drop=True)
    except Exception as e:
        print(f"General error fetching data from {exchange_id}: {e}")
        return pd.DataFrame()

def get_pairs(symbols):
    pairs = []
    for i in range(len(symbols)):
        for j in range(i + 1, len(symbols)):
            pair = {'Asset1': symbols[i], 'Asset2': symbols[j]}
            pairs.append(pair)
    return pairs


def trade(prices, bid_ask_df, pairs, threshold, position_size, stop_loss_limit, profit_limit, maker_fee):
    pnl_list = []
    positions = {}
    global_cum_pnl = 0  # Initialize cumulative PnL as a global variable
    
    # Adjust limits and fees to decimal form
    stop_loss_limit /= 100
    profit_limit /= 100
    maker_fee /= 100

    for pair in pairs:
        asset1, asset2 = pair['Asset1'], pair['Asset2']
        symbol_pair = f"{asset1}-{asset2}"
        
        if symbol_pair not in positions:
            positions[symbol_pair] = {'open': False, 'entry_price': 0, 'lots': 0}

        # Calculate price ratios using 'close' prices
        if asset1 in prices.columns and asset2 in prices.columns:
            price_ratios = prices[asset1] / prices[asset2]
            z_scores = zscore(price_ratios.dropna())

            for i, z_score in enumerate(z_scores):
                timestamp = prices.index[i]  # Assuming 'prices' DataFrame has timestamps as its index
                position = positions[symbol_pair]

                # Find the latest bid-ask data for asset1
                latest_bid_ask = bid_ask_df[bid_ask_df['symbol'] == asset1].iloc[-1]

                if not position['open'] and z_score < -threshold:
                    # Set entry_price to the ask price from bid_ask_df
                    entry_ask_price = latest_bid_ask['ask']
                    if entry_ask_price > 0:
                        position['open'] = True
                        position['entry_price'] = entry_ask_price
                        position['lots'] = position_size / entry_ask_price
                        pnl_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': 'Open Position',
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Entry Price': entry_ask_price, 'Lots': position['lots'], 'PnL': '',
                            'Cumulative PnL': global_cum_pnl
                        })

                elif position['open']:
                    # Set exit_price to the bid price from bid_ask_df
                    exit_bid_price = latest_bid_ask['bid']
                    change_percentage = (exit_bid_price - position['entry_price']) / position['entry_price']
                    if change_percentage <= -stop_loss_limit or change_percentage >= profit_limit:
                        position['open'] = False
                        pnl = position['lots'] * (exit_bid_price - position['entry_price']) - maker_fee * position_size
                        global_cum_pnl += pnl
                        action = 'Closed with Stop Loss' if change_percentage <= -stop_loss_limit else 'Closed with Profit'
                        pnl_list.append({
                            'Pair': symbol_pair, 'Timestamp': timestamp, 'Action': action,
                            'Z-Score': z_score, 'Strategy': 'One-sided', 'Exit Price': exit_bid_price, 'PnL': pnl,
                            'Cumulative PnL': global_cum_pnl
                        })

    return pd.DataFrame(pnl_list)


def get_bid_ask(exchange_id, symbols):
    live_data = []

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
            
            live_data.append([symbol, timestamp_iso, top_bid, top_ask, exchange_id])
            print(f"Completed download for {symbol} on {exchange_id}")
        except Exception as e:
            print(f"Error fetching data for {symbol} on {exchange_id}: {e}")

    return live_data

def main(exchange_id='bitstamp'):
    while True:
        prices_df = get_prices(exchange_id, symbols, timeframe, days)     
        bid_ask = get_bid_ask(exchange_id, symbols)
        # Convert to DataFrame
        bid_ask_df = pd.DataFrame(bid_ask, columns=['symbol', 'timestamp', 'bid', 'ask', 'exchange'])
        asset_pairs = get_pairs(symbols)
        pnl_df = trade(prices_df, bid_ask_df, asset_pairs, zthreshold, position_size, stop_loss_limit, profit_limit, maker_fee)
        try:
            # Attempt to write the fetched data to the database
            # db_util.write_bid_ask(df)
             #file_util.write_csv(prices_df, 'bitstamp_prices.csv')
             #file_util.write_csv(bid_ask_df, 'bitstamp_bid_ask.csv')
            file_util.write_csv(pnl_df, 'bitstamp_pnl.csv')
            print('Successfully wrote to file')
        except Exception as e:
            # Handle database-related exceptions
            print(f'Failed to write to database: {e}')

        time.sleep(60)  # Sleep for 60 seconds before the next fetch

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download order book data.')
    parser.add_argument('-e', '--exchange', default='bitstamp', help='Exchange ID (default: bitstamp)')
    args = parser.parse_args()

    main(args.exchange)
