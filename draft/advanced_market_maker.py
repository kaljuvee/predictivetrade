import ccxt
import numpy as np
import threading
import time
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Crypto Market Making Bot')
parser.add_argument('-e', '--exchange', help='Exchange name (e.g., binance, bitstamp)', required=True)
parser.add_argument('-s', '--symbol', help='Symbol for trading (e.g., BTC/USD)', required=False, default='BTC/USD')
parser.add_argument('-a', '--amount', help='Amount to trade', required=False, default=0.01, type=float)
parser.add_argument('-sm', '--side_mode', help='Trading side mode (one-sided or two-sided)', required=False, default='two-sided', choices=['one-sided', 'two-sided'])
parser.add_argument('-m', '--mode', help='Trading mode (live or paper)', required=False, default='live', choices=['live', 'paper'])
parser.add_argument('-st', '--strategy', help='Bid-ask adjustment strategy', required=False, default='adjust_bid_ask', choices=['adjust_bid_ask', 'adjust_order_book_imbalance'])
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
strategy = args.strategy  # Use the parsed position_size argument

# Global variable to track the current position size and P&L
current_position_size = position_size
pnl = 0.0
# Global variables to track state
is_position_open = False  # Tracks whether we have an open position
last_order_side = 'sell'  # Tracks the side of the last filled orde
# Assuming a DataFrame to track PnL and positions has been initialized

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

def adjust_bid_ask(bid_price, ask_price, spread_capture_ratio=0.5):
    """Adjust bid and ask prices based on the bid-ask spread."""
    spread = ask_price - bid_price
    adjusted_bid = ask_price - spread * spread_capture_ratio
    adjusted_ask = bid_price + spread * spread_capture_ratio
    return adjusted_bid, adjusted_ask

def adjust_order_book_imbalance(bid_volume, ask_volume, adjusted_bid, adjusted_ask, imbalance_threshold=0.2):
    """Adjust order levels based on order book imbalance."""
    total_volume = bid_volume + ask_volume
    imbalance = abs(bid_volume - ask_volume) / total_volume

    if imbalance > imbalance_threshold:
        if bid_volume > ask_volume:
            # More volume on the bid side, increase the bid price to be more aggressive
            adjusted_bid *= 1.01  # Increase by 1%
        else:
            # More volume on the ask side, decrease the ask price to be more aggressive
            adjusted_ask *= 0.99  # Decrease by 1%

    return adjusted_bid, adjusted_ask

def adjust_volatility(recent_price_changes, adjusted_bid, adjusted_ask, volatility_threshold=0.02):
    """Adjust order levels based on market volatility."""
    volatility = np.std(recent_price_changes)

    if volatility > volatility_threshold:
        # In high volatility, widen the spread to reduce risk
        adjusted_bid *= 0.99  # Decrease by 1%
        adjusted_ask *= 1.01  # Increase by 1%

    return adjusted_bid, adjusted_ask

def adjust_order_levels(order_book, strategy, side_mode, volume_threshold=0.2):
    """Adjust bid/ask levels based on the selected strategy and side mode."""
    top_bid, top_ask = order_book['bids'][0][0], order_book['asks'][0][0]
    bid_volume, bid_price = get_cumulative_depth(order_book['bids'])
    ask_volume, ask_price = get_cumulative_depth(order_book['asks'])

    # Initial strategy-based adjustment
    if strategy == 'adjust_bid_ask':
        adjusted_bid, adjusted_ask = adjust_bid_ask(top_bid, top_ask)
    #elif strategy == 'adjust_volatility':
        # You need to define how to calculate recent_price_changes for your strategy
    #    adjusted_bid, adjusted_ask = adjust_volatility(recent_price_changes, top_bid, top_ask)
    elif strategy == 'adjust_order_book_imbalance':
        adjusted_bid, adjusted_ask = adjust_order_book_imbalance(bid_volume, ask_volume, top_bid, top_ask)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Further adjustment based on side_mode and volume imbalance
    if side_mode == 'two-sided':
        if bid_volume > ask_volume + volume_threshold:
            adjusted_bid = bid_price + 1  # Increase bid price to be more aggressive
            # Keep the adjusted ask price from the strategy adjustment
        elif ask_volume > bid_volume + volume_threshold:
            # Keep the adjusted bid price from the strategy adjustment
            adjusted_ask = ask_price - 1  # Decrease ask price to be more aggressive
        # If volumes are balanced, keep the strategy-adjusted prices
    else:  # one-sided mode
        if bid_volume > ask_volume + volume_threshold:
            adjusted_bid = bid_price + 1  # Increase bid price to be more aggressive
            adjusted_ask = None  # Do not place an ask order
        else:
            adjusted_bid = None  # Do not place a bid order
            adjusted_ask = ask_price - 1  # Decrease ask price to be more aggressive

    return adjusted_bid, adjusted_ask

def place_orders(mode, side_mode, strategy):
    """Place bid and ask orders based on the current order book, trading mode, side mode, and strategy."""
    global is_position_open, last_order_side

    try:
        order_book = exchange.fetch_order_book(symbol)
        
        # Adjust bid and ask levels based on the selected strategy and side mode
        adjusted_bid, adjusted_ask = adjust_order_levels(order_book, strategy, side_mode)

        if side_mode == 'two-sided':
            # In two-sided mode, place both buy and sell orders based on adjusted bid and ask
            bid_price = adjusted_bid if adjusted_bid is not None else order_book['bids'][0][0]  # Fallback to top bid if None
            ask_price = adjusted_ask if adjusted_ask is not None else order_book['asks'][0][0]  # Fallback to top ask if None

            if mode == 'live':
                # Place live orders on the exchange
                buy_order = exchange.create_limit_buy_order(symbol, amount, bid_price)
                sell_order = exchange.create_limit_sell_order(symbol, amount, ask_price)
                print(f"Live buy order placed at {bid_price}, sell order placed at {ask_price}")
            else:
                # Simulate order placement for paper trading
                print(f"Paper trading: Would place buy order at {bid_price} and sell order at {ask_price}")

        elif side_mode == 'one-sided':
            # In one-sided mode, place either a buy or sell order based on volume imbalance
            if adjusted_bid is not None:
                # Place a buy order
                order_price = adjusted_bid
                order_side = 'buy'
            elif adjusted_ask is not None:
                # Place a sell order
                order_price = adjusted_ask
                order_side = 'sell'
            else:
                # No order to place if both adjusted_bid and adjusted_ask are None
                print("No order to place based on current market conditions and strategy.")
                return

            if mode == 'live':
                # Place the live order on the exchange
                if order_side == 'buy':
                    order = exchange.create_limit_buy_order(symbol, amount, order_price)
                else:
                    order = exchange.create_limit_sell_order(symbol, amount, order_price)
                print(f"Live {order_side} order placed at {order_price}")
                
            else:
                # Simulate order placement for paper trading
                print(f"Paper trading: Would place {order_side} order at {order_price}")
                

    except Exception as e:
        print(f"An error occurred in place_orders: {e}")


def main():
    """Main function to run the market making bot."""
    while True:
        place_orders(mode, side_mode, strategy)
        time.sleep(10)  # Wait for 20 seconds before next run

# Run the main function in a separate thread
thread = threading.Thread(target=main)
thread.start()

