import ccxt

def check_token(token):
  exchange = ccxt.binance()
  token = token + '/USDT'
  try:
    ticker = exchange.fetch_ticker(token)
    return True
  except:
    return False