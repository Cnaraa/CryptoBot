import ccxt

def check_token(token):
  if token == 'USDT':
    return 1.0
  exchange = ccxt.binance()
  token = token + '/USDT'
  try:
    ticker = exchange.fetch_ticker(token)
    return ticker['last']
  except:
    return False
