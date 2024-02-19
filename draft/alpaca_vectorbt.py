import vectorbt as vbt

API_KEY = 'PKWSHV3AS4J71TGOQEOC'
SECRET_KEY = 'wffi5PYdLHI2N/6Kfqx6LBTuVlfURGgOp9u5mXo5'

vbt.settings.data['alpaca']['key_id'] = API_KEY
vbt.settings.data['alpaca']['secret_key'] = SECRET_KEY

alpacadata = vbt.AlpacaData.Download(symbol='AAPL', start='4 days ago UTC`, end=`1 day ago UTC`, timeframe='1h')

data = alpaca.get_data()
print(data)
