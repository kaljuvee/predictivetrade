import ccxt
import pandas as pd
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Exchange operations')
parser.add_argument('-e', '--exchange', help='Exchange name (e.g., binance, bitstamp)', required=True)
parser.add_argument('-s', '--symbol', help='Symbol for price data (e.g., BTC/USDT)', required=False, default='BTC/USDT')
args = parser.parse_args()

# Initialize exchange clients (ensure API keys are securely configured)
exchanges = {
    'bitstamp': ccxt.bitstamp({'apiKey': 'N5iTaKfNCuzJIlgaRkYtv57yue19LPWk', 'secret': 'a9PMzU4DL7oSlcNQzEAG0EXQPqAGDuB1', 'uid': '12867'}),
    'binance': ccxt.binance({'apiKey': 'YOUR_API_KEY', 'secret': 'YOUR_SECRET'}),
    'kraken': ccxt.kraken({'apiKey': 'JGKRYMMLXbi77letWZ7TxzR7GWGaOhHhFt17vmohGEVu2oiM8E1JZJpZ', 'secret': 'ZtC+QrQMmD9TDrLX9QS6HcsW88gynUqejCzP4L+5ak5+Zwg7To7nlbexAzJa9AsNsA18CduR1dXTSZnukfHmuA=='}),
    'poloniex': ccxt.poloniex({'apiKey': 'IZ15YKXT-8N0UY64A-WINWKNFV-URKTVZ73', 'secret': 'd5a29ae3ba64464e41355e6d10453f743ef9edcf1dcd76987d302073ac7556feb4e5d33ad1707204d6a491d434d8ee117167bcbf0a7bc77d4eae9695e4752374'})
}

def fetch_price(exchange_id, symbol=args.symbol):
    """Fetch the latest price for a given symbol from an exchange."""
    exchange = exchanges[exchange_id]
    ticker = exchange.fetch_ticker(symbol)
    return ticker['last'], symbol  # Returns the last traded price

def list_amount_value(exchange_id, symbol=args.symbol):
    """List the value of holdings for a given symbol."""
    exchange = exchanges[exchange_id]
    balance = exchange.fetch_balance()
    if symbol.split('/')[0] in balance:
        amount = balance[symbol.split('/')[0]]['total']
        price = fetch_price(exchange_id, symbol)
        position_value = amount * price
        return position_value
    else:
        return 0

def cancel_order(exchange_id, order_id):
    """Cancel an order on a given exchange."""
    exchange = exchanges[exchange_id]
    return exchange.cancel_order(order_id)

def place_order(exchange_id, order_type, amount, price=None, symbol=args.symbol):
    """
    Place an order on a given exchange.
    """
    exchange = exchanges[exchange_id]

    if order_type == 'market':
        return exchange.create_market_order(symbol, 'buy', amount)
    elif order_type == 'limit':
        if price is None:
            raise ValueError("Price must be specified for limit orders.")
        return exchange.create_limit_order(symbol, 'buy', amount, price)
    else:
        raise ValueError("Invalid order type. Use 'market' or 'limit'.")

# Example usage (uncomment and modify with caution)
exchange_name = args.exchange
symbol = args.symbol
print('latest_price: ', fetch_price(exchange_name, symbol))
print('position_value: ', list_amount_value(exchange_name, symbol))
# place_order(exchange_name,'limit', 0.001, 50000, symbol)
# cancel_order(exchange_name, 'ORDER_ID')

