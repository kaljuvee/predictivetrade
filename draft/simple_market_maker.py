import ccxt
import numpy as np
import threading
import time
import argparse
from util import pnl_util

# Parse command line arguments
parser = argparse.ArgumentParser(description='Crypto Market Making Bot')
parser.add_argument('-e', '--exchange', help='Exchange name (e.g., binance, bitstamp)', required=True)
parser.add_argument('-s', '--symbol', help='Symbol for trading (e.g., BTC/USD)', required=False, default='BTC/USD')
parser.add_argument('-a', '--amount', help='Amount to trade', required=False, default=0.01, type=float)
parser.add_argument('-sm', '--side_mode', help='Trading side mode (one-sided or two-sided)', required=False, default='two-sided', choices=['one-sided', 'two-sided'])
parser.add_argument('-m', '--mode', help='Trading mode (live or paper)', required=False, default='live', choices=['live', 'paper'])
parser.add_argument('-p', '--position_size', help='Initial position size in USD', required=False, default=10000, type=float)
args = parser.parse_args()



# Initialize exchange clients (ensure API keys are securely configured)
exchanges = {
    'bitstamp': ccxt.bitstamp({'apiKey': 'N5iTaKfNCuzJIlgaRkYtv57yue19LPWk', 'secret': 'a9PMzU4DL7oSlcNQzEAG0EXQPqAGDuB1', 'uid': '12867'}),
    'binance': ccxt.binance({'apiKey': 'YOUR_API_KEY', 'secret': 'YOUR_SECRET'}),
    'kraken': ccxt.kraken({'apiKey': 'JGKRYMMLXbi77letWZ7TxzR7GWGaOhHhFt17vmohGEVu2oiM8E1JZJpZ', 'secret': 'ZtC+QrQMmD9TDrLX9QS6HcsW88gynUqejCzP4L+5ak5+Zwg7To7nlbexAzJa9AsNsA18CduR1dXTSZnukfHmuA=='}),
    'poloniex': ccxt.poloniex({'apiKey': 'IZ15YKXT-8N0UY64A-WINWKNFV-URKTVZ73', 'secret': 'd5a29ae3ba64464e41355e6d10453f743ef9edcf1dcd76987d302073ac7556feb4e5d33ad1707204d6a491d434d8ee117167bcbf0a7bc77d4eae9695e4752374'})
}

if args.exchange not in exchanges:
    raise ValueError("Exchange not supported or not defined in the script.")

exchange = exchanges[args.exchange]
symbol = args.symbol  # Use the parsed symbol argument
amount = args.amount  # Use the parsed amount argument
side_mode = args.side_mode  # Use the parsed side_mode argument
mode = args.mode  # Use the parsed mode argument
position_size = args.position_size  # Use the parsed position_size argument

# Global variable to track the current position size and P&L
current_position_size = position_size
pnl = 0.0
cumulative_pnl = 0.0
# Global variables to track state
is_position_open = False  # Tracks whether we have an open position
last_order_side = 'sell'  # Tracks the side of the last filled orde
strategy = 'market-making-basic'

def calculate_pnl(fill_price, side):
    """Calculate new position size and P&L based on the fill."""
    global current_position_size, pnl
    try:
        trade_value = fill_price * amount
        if side == 'buy':
            current_position_size -= trade_value
            pnl -= trade_value  # Assuming buying reduces P&L
        elif side == 'sell':
            current_position_size += trade_value
            pnl += trade_value  # Assuming selling increases P&L
        print(f"New position size: {current_position_size} USD, P&L: {pnl} USD")
        return pnl
    except Exception as e:
        print(f"Error in calculating P&L: {e}")

def get_cumulative_depth(order_book_side, depth=10):
    """
    Calculate the cumulative volume and average price up to a certain depth.
    :param order_book_side: List of orders (bids or asks) from the order book.
    :param depth: Number of levels to include.
    :return: Cumulative volume and weighted average price up to the specified depth.
    """
    total_volume = sum([order[1] for order in order_book_side[:depth]])
    weighted_avg_price = np.average([order[0] for order in order_book_side[:depth]], weights=[order[1] for order in order_book_side[:depth]])
    return total_volume, weighted_avg_price


def place_orders(mode, side_mode):
    """Place bid and ask orders based on the current order book, trading mode, and side mode."""
    global is_position_open, last_order_side, cumulative_pnl  # Declare global variables
    try:
        order_book = exchange.fetch_order_book(symbol)
        top_bid, top_ask = order_book['bids'][0][0], order_book['asks'][0][0]

        # Determine the price and side for the next order
        if not is_position_open or last_order_side == 'sell':
            # Place a buy order at the top ask price if we don't have an open position or the last order was a sell
            order_price = top_ask
            order_side = 'buy'
        else:
            # Place a sell order at the top bid price if we have an open position and the last order was a buy
            order_price = top_bid
            order_side = 'sell'

        # Calculate the USD value of the order
        order_value_usd = order_price * amount
        print(f"Placing a {order_side} order for {amount} lots ({order_value_usd} USD) at {order_price}")

        if mode == 'live':
            if order_side == 'buy':
                order = exchange.create_limit_buy_order(symbol, amount, order_price)
            else:
                order = exchange.create_limit_sell_order(symbol, amount, order_price)
            print(f"Live {order_side} order placed:", order)
            is_position_open = (order_side == 'buy')
            last_order_side = order_side
        else:  # paper trading
            print(f"Paper trading mode - {order_side} order not sent to exchange.")
            # Simulate order fill immediately for paper trading
            print(f"Paper {order_side} order would have been filled at: {order_price}")
            pnl = calculate_pnl(order_price, order_side)
            cumulative_pnl = cumulative_pnl + pnl
            print('PnL:', pnl)
            pnl_util.write_pnl(symbol, order_side, strategy, order_price, amount, pnl, cumulative_pnl)
            is_position_open = (order_side == 'buy')
            last_order_side = order_side

    except Exception as e:
        print(f"An error occurred in place_orders: {e}")

def main():
    """Main function to run the market making bot."""
    while True:
        place_orders(mode, side_mode)
        time.sleep(20)  # Wait for 20 seconds before next run

# Run the main function in a separate thread
thread = threading.Thread(target=main)
thread.start()

