import ccxt
import time


def main():
    exchange = ccxt.binance()
    while True:
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(ticker["last"])
        time.sleep(5)


if __name__ == '__main__':
    main()
