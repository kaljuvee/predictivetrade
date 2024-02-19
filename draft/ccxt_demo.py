import ccxt
import pandas as pd

# Initialize the exchange
exchange = ccxt.binance({
    'rateLimit': 1200,  # Binance rate limit
    'enableRateLimit': True,  # Enable built-in rate limit
})

# List of symbols to fetch data for
symbols = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'SOL/USDT',
    'ADA/USDT', 'AVAX/USDT', 'DOGE/USDT', 'DOT/USDT', 'MATIC/USDT',
    'SHIB/USDT', 'LTC/USDT', 'UNI/USDT', 'LINK/USDT', 'TRX/USDT',
    'BCH/USDT', 'XLM/USDT', 'ETC/USDT', 'FIL/USDT', 'VET/USDT'
]

# Fetch the ticker data for each symbol
data = []
for symbol in symbols:
    ticker = exchange.fetch_ticker(symbol)
    data.append({
        'symbol': symbol,
        'datetime': ticker['datetime'],
        'high': ticker['high'],
        'low': ticker['low'],
        'bid': ticker['bid'],
        'ask': ticker['ask'],
        'last': ticker['last'],
        'baseVolume': ticker['baseVolume'],
        'quoteVolume': ticker['quoteVolume'],
        'percentage': ticker['percentage'],
    })

# Convert the list of data to a pandas DataFrame
df = pd.DataFrame(data)

print(df)
