import ccxt
import pandas as pd
import exchange_util
import argparse

def main(exchange_id):
    symbols = exchange_util.get_top_coins_by_volume(exchange_id, 20)
    print('Top symbols', symbols)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download order book data.')
    parser.add_argument('-e', '--exchange', default='bitstamp', help='Exchange ID (default: bitstamp)')
    args = parser.parse_args()

    main(args.exchange)