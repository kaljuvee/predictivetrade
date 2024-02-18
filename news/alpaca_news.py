import websocket
import json
import pandas as pd


API_KEY = 'PKWSHV3AS4J71TGOQEOC'
SECRET_KEY = 'wffi5PYdLHI2N/6Kfqx6LBTuVlfURGgOp9u5mXo5'

file_path = 'alpaca_news.csv'

# Define the callback for handling received messages
def on_message(ws, message):
    data = json.loads(message)  # Convert the received message (JSON string) to a Python dictionary
    
    # Assuming the news data is present in a key named 'news' (adjust based on actual structure)
    if 'news' in data:
        news_item = data['news']
        print(f"Received News Item:\n{news_item}\n")
        df = pd.DataFrame(news_item)
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            df.to_csv(file_path, mode='a', header=False, index=False)
        else:
            df.to_csv(file_path, index=False)
    else:
        print(f"Received: {message}")  # Print the entire message if it doesn't contain a news key


# Define the callback for handling errors
def on_error(ws, error):
    print(f"Error: {error}")

# Define the callback for opening the connection
def on_open(ws):
    # Authentication
    auth_data = {
        "action": "auth",
        "key": API_KEY,
        "secret": SECRET_KEY
    }
    ws.send(json.dumps(auth_data))
    
    # Subscription
    # Uncomment one of the following lines based on your subscription choice:

    # Subscribe to all stock and crypto symbols
    ws.send(json.dumps({"action": "subscribe", "news": ["*"]}))
    
    # OR Subscribe to specific stock symbols
    #ws.send(json.dumps({"action": "subscribe", "news": ["AAPL", "TSLA"]}))

# Define the callback for closing the connection
def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def main():
    # Create a WebSocket connection
    ws = websocket.WebSocketApp(
        "wss://stream.data.alpaca.markets/v1beta1/news",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

if __name__ == '__main__':
    main()