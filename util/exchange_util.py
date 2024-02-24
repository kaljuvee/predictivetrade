import pandas as pd
import ccxt
import math
import yfinance as yf
import yaml
from datetime import datetime, timedelta

# Usage
yaml_file_path = 'config/biotech.yaml'

#biotech_symbols = ['IBB', 'XBI', 'FBT', 'BBH', 'ARKG', 'FBIO', 'KA', 'QGEN', 'DYAI', 'JSPR', 'ANAB', 'ECOR', 'ELOX', 'MDWD', 'RAD.AX', 'EYEN', 'PYPD', 'SCLX', 'TALS', 'SNCE', 'ORIC', 'TTOO', 'ADXN', 'SPRY', 'IMNN', 'ADTX', 'OCUP', 'ARQT', 'IMCR', 'ORPHA.CO', 'VIR', 'DBVT', 'ICCC', 'ONCT', 'ALVO', 'EVAX', 'CHRS', 'MYNZ', 'SCPH', 'MDAI', 'BIOR', 'MLYS', 'LGVN', 'BMRA', 'KRON', 'CDTX', 'NTLA', 'TLSA', 'PCIB.OL', 'SANN.SW', 'IMRX', 'OPGN', 'TGTX', 'VBLT', 'ANVS', 'ADAG', 'INAB', 'PCRX', 'BCAB', 'WINT', 'KBLB', 'PEPG', 'NSPR', 'NZYM-B.CO', 'MYCO.CN', 'NANO.PA', 'CERT', 'AKYA', 'ALERS.PA', 'VALN', 'MLTX', 'RENB', 'RVVTF', 'YTEN', 'RZLT', 'ELTX', 'NKGN', 'FARON.HE', 'CCCC', 'BCDA', 'MNOV', 'OXUR.BR', 'CAPR', 'OVID', 'TSHA', 'BTAI', 'AKRO', 'OCGN', 'CNTG', 'OCS', 'ANNX', 'MYCOF', 'HARP', 'MDXH', 'VXRT', 'IMMX', 'GTHX', 'INMB', 'HUMA', 'PHIL.MI', 'IOVA', 'CRSP', 'TOVX', 'EDIT', 'RAIN', 'CFRX', 'PCVX', 'RNAZ', 'NOTV', 'CRBP', 'IMMP', 'ENTX', 'BNOX', 'MDG1.DE', 'BNTX', 'NEXI', 'CADL', 'CELU', 'RAPT', 'CKPT', 'XFOR', 'BXRX', 'CBAY', 'PHGE', 'HOOK', 'BIOS.BR', 'XXII', 'CDMO', 'NXTC', 'ETNB', 
#               'NKTX', 'GLUE', 'EVLO', 'ACIU', 'GMAB', 'PLRX', 'STRO', 'SWAV', 'SEER', 'AEON', 'CTKB', 'GRFS', 'AMRN', 'BIIB', 'BIVI', 'CTMX', 'SGMT', 'BICX', 'STTK', 'XBIT', 'VINC', 'APTO', 'FGEN', 'GLPG', 'TCRX', 'ADPT', 'SWTX']

def get_biotech_symbols():
    try:
        # Open and read the YAML file
        with open(yaml_file_path, 'r') as file:
            data = yaml.safe_load(file)
        
        # Get the keys from the YAML data
        symbols = list(data.keys())
        
        return symbols
    except Exception as e:
        print(f"Error reading YAML file: {e}")
        return []
    
biotech_symbols=get_biotech_symbols()

def get_prices_yfinance(selected_symbols, interval='1d', days=30):
    try:
        all_data = pd.DataFrame()
        
        # Ensure 'days' is an integer
        days = int(days)

        # Calculate start date based on the number of days to go back
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Format the dates as strings
        formatted_start_date = start_date.strftime('%Y-%m-%d')
        formatted_end_date = end_date.strftime('%Y-%m-%d')
        
        for symbol in selected_symbols:
            # Fetch the data for the given symbol, interval, and date range
            data = yf.download(symbol, interval=interval, start=formatted_start_date, end=formatted_end_date)
            
            # Create a new 'timestamp' column based on the DataFrame's index
            data['timestamp'] = data.index
            
            # Reset the index without keeping the original index column
            data.reset_index(drop=True, inplace=True)
            
            # Drop the 'Close' column
            data.drop(columns=['Close'], inplace=True)
            
            # Rename 'Adj Close' to 'Close'
            data.rename(columns={'Adj Close': 'Close'}, inplace=True)
            
            # Lowercase all column names
            data.columns = data.columns.str.lower()
            
            data['symbol'] = symbol  # Add the symbol column
            all_data = pd.concat([all_data, data], ignore_index=True)  # Concatenate to the all_data DataFrame
        
        return all_data.sort_values(by='timestamp').reset_index(drop=True)  # Sort by 'timestamp' and reset index
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()

# Example usage:
# selected_symbols = ['AAPL', 'MSFT']
# period = '1mo'  # '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
# interval = '1d'  # Valid intervals: '1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo'
# prices = get_prices_yfinance(selected_symbols, period, interval)


def get_bid_ask(all_data, spread_percentage):
    all_data['bid'] = all_data['close'] * (1 - 0.5 * spread_percentage / 100)
    all_data['ask'] = all_data['close'] * (1 + 0.5 * spread_percentage / 100)
    return all_data[['symbol', 'timestamp', 'bid', 'ask', 'close']]
    
def get_top_coins_by_volume(exchange_id, limit = 15):
    try:
        # Initialize the exchange
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()

        # Load markets
        exchange.load_markets()

        # Fetch ticker information for all symbols
        tickers = exchange.fetch_tickers()

        # Sort the tickers by volume and get the top 10
        sorted_tickers = sorted(tickers.values(), key=lambda x: x['quoteVolume'], reverse=True)[:limit]

        # Create a list of top coins with their volumes
        top_coins = [ticker['symbol'] for ticker in sorted_tickers]
        return top_coins
    except Exception as e:
        return str(e)

def get_symbols_usd(exchange_id):
    try:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        all_symbols = exchange.load_markets().keys()

        # Specify the base currencies you want to exclude
        excluded_base_currencies = ['GBP', 'EUR', 'CHF']

        # Filter to include only symbols that are paired with USD or USDT, but not with the excluded base currencies
        filtered_symbols = [
            symbol for symbol in all_symbols 
            if (symbol.endswith('/USD') or symbol.endswith('/USDT')) and not any(symbol.startswith(excluded_base + '/') for excluded_base in excluded_base_currencies)
        ]

        return filtered_symbols, None  # Return symbols and no error
    except Exception as e:
        return [], str(e)  # Return empty list and error message

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
            for i in range(number_of_calls):
                since = exchange.milliseconds() - (86400000 * days) + (i * limit_per_call * interval_in_milliseconds)
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit_per_call)
                data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
                data['symbol'] = symbol
                all_data = pd.concat([all_data, data], ignore_index=True)
                
        return all_data.sort_values(by='timestamp').reset_index(drop=True)
    except Exception as e:
        print(f"Error fetching data from {exchange_id}: {e}")
        return pd.DataFrame()

def get_prices_old(exchange_id, selected_symbols, timeframe):
    try:
        # Dynamically create an exchange instance based on the exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class()
        
        all_data = pd.DataFrame()

        for symbol in selected_symbols:
            limit = 1440  # Maximum number of data points
            since = exchange.milliseconds() - 86400000  # Last 24 hours
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since, limit)
            data = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            data['timestamp'] = pd.to_datetime(data['timestamp'], unit='ms')
            data['symbol'] = symbol
            all_data = pd.concat([all_data, data])

        return all_data
    except Exception as e:
        st.error(f"Error fetching data from {exchange_id}: {e}")
        return pd.DataFrame()
