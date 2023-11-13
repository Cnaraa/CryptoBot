import ccxt
import time


def main():
    token = input('Введите название валюты: ')
    token = token + '/USDT'
    exchange = ccxt.binance()
    while True:
        try:
            ticker = exchange.fetch_ticker(token)
            print(ticker["last"])
            time.sleep(5)
        except:
            print('Монета не найдена на бирже')


if __name__ == '__main__':
    main()
