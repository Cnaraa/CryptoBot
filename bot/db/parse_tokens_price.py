import time
import ccxt
import sqlite3


def main():
    with sqlite3.connect('crypto.db') as connection:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT token_name FROM users_portfolio GROUP BY token_name
""")
        result = cursor.fetchall()
        print(result)
        for token in result:
          if token[0] == 'USDT':
            token_price = 1.0
          else:
            exchange = ccxt.binance()
            ticker = exchange.fetch_ticker(token[0] + '/USDT')
            token_price = ticker['last']
          cursor.execute("""
              REPLACE INTO tokens_price (token_name, price) VALUES (?, ?) 
""", (token[0], token_price))
          connection.commit()


if __name__ == '__main__':
    while True:
        main()
        time.sleep(5)