import sqlite3
from check_token import check_token
import tabulate

'''
with sqlite3.connect('crypto.db') as connection:
  cursor = connection.cursor()

  cursor.execute("""
      CREATE TABLE users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER UNIQUE
        )
  """)

  cursor.execute("""
      CREATE TABLE users_portfolio (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          token_name VARCHAR(255),
          token_amount DECIMAL(10, 10),
          average_price DECIMAL(10, 2),
          FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
  """)

'''
def check_id_in_database(new_token):
  with sqlite3.connect('crypto.db') as connection:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT user_id FROM users WHERE user_id = (?)
""", (new_token['user_id'],))
    result = cursor.fetchone()
    if result is None:
      cursor.execute("""
          INSERT INTO users VALUES (NULL, (?))
""", (new_token['user_id'],))
      connection.commit()
      add_new_token(new_token)
    else:
      check_token_in_portfolio(new_token)
  return True


def add_new_token(new_token):
  with sqlite3.connect('crypto.db') as connection:
     cursor = connection.cursor()
     cursor.execute("""
        INSERT INTO users_portfolio (id, user_id, token_name, token_amount, average_price)
        VALUES (NULL, ?, ?, ?, ?)
""", (new_token['user_id'], new_token['token_name'], new_token['token_amount'], new_token['token_price']))
     connection.commit()
  return True


def check_token_in_portfolio(new_token):
  with sqlite3.connect('crypto.db') as connection:
    cursor = connection.cursor()
    if new_token['action'] == 'buy':
      cursor.execute("""
          SELECT token_amount FROM users_portfolio WHERE user_id = (?) and token_name = (?)
""", (new_token['user_id'], 'USDT'))
      result = cursor.fetchone()
      if result[0] > (new_token['token_price'] * new_token['token_amount']):
        cursor.execute("""
            UPDATE users_portfolio SET token_amount = (?), average_price = (?) WHERE user_id = (?) and token_name = (?)
""", (result[0] - (new_token['token_price'] * new_token['token_amount']),
      1.0,
      new_token['user_id'],
      'USDT',))
        connection.commit()
        cursor.execute("""
            SELECT * FROM users_portfolio WHERE user_id = (?) and token_name = (?) 
""", (new_token['user_id'], new_token['token_name']))  
        result = cursor.fetchone()
        if result: # TODO - repeat func
          token_amount = result[3] + new_token['token_amount']
          average_price = round(((result[4]*result[3]) + (new_token['token_amount'] * new_token['token_price'])) / (result[3] + new_token['token_amount']), 2)
          cursor.execute("""
              UPDATE users_portfolio SET token_amount = (?), average_price = (?) WHERE user_id = (?) and token_name = (?)
    """, (token_amount, average_price, new_token['user_id'], new_token['token_name']))
          connection.commit()
        else:
          add_new_token(new_token)
        return True
      else:
        return False
    else:
      cursor.execute("""
          SELECT * FROM users_portfolio WHERE user_id = (?) and token_name = (?)
  """, (new_token['user_id'], new_token['token_name']))
      result = cursor.fetchone()
      if new_token['action'] == 'add':
        if result is None:
          add_new_token(new_token)
        else:
          token_amount = result[3] + new_token['token_amount']
          average_price = round(((result[4]*result[3]) + (new_token['token_amount'] * new_token['token_price'])) / (result[3] + new_token['token_amount']), 2)
          cursor.execute("""
              UPDATE users_portfolio SET token_amount = (?), average_price = (?) WHERE user_id = (?) and token_name = (?)
    """, (token_amount, average_price, new_token['user_id'], new_token['token_name']))
          connection.commit()
        return True
      elif new_token['action'] == 'sell':
        if result is None:
          return False
        else:
          return True
      else:
        return False
    

def sell_token(new_token):
  with sqlite3.connect('crypto.db') as connection:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT token_amount FROM users_portfolio WHERE user_id = (?) and token_name = (?)
""", (new_token['user_id'], new_token['token_name']))
    result = cursor.fetchone() #TODO - добавить проверку
    cursor.execute("""
        UPDATE users_portfolio SET token_amount = (?) WHERE user_id = (?) and token_name = (?) 
""", ((result[0] - new_token['token_amount']),
      new_token['user_id'], new_token['token_name']))
    connection.commit()
    cursor.execute("""
        SELECT token_amount FROM users_portfolio WHERE user_id = (?) and token_name = (?)
""", (new_token['user_id'], 'USDT'))
    result = cursor.fetchone()
    if result: # TODO
      cursor.execute("""
          UPDATE users_portfolio SET token_amount = (?) WHERE user_id = (?) and token_name = (?)
""", (result[0] + (new_token['token_amount'] * new_token['token_price']),
      new_token['user_id'], 'USDT'))
      connection.commit()
    else:
      cursor.execute("""
          INSERT INTO users_portfolio (id, user_id, token_name, token_amount, average_price)
          VALUES (NULL, ?, ?, ?, ?)
  """, (new_token['user_id'], 'USDT', (new_token['token_amount'] * new_token['token_price']), 1.0))
    connection.commit()
  return True


def get_user_portfolio(user_id):
  with sqlite3.connect('crypto.db') as connection:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM users_portfolio WHERE user_id = (?)
""", (user_id, ))
    result = cursor.fetchall()
    user_portfolio = {}
    token = {}
    for token_info in result:
      token['token_amount'] = token_info[3]
      last_token_price = check_token(token_info[2])
      token_value = round(token_info[3] * last_token_price, 2)
      token['token_value'] = token_value
      token['financial_results'] = ((token_value - (token_info[3] * token_info[4])) / (token_info[3] * token_info[4]))
      token['financial_results_percentages'] = round(token['financial_results'] * 100, 2)
      token['financial_results'] = round((token_info[3] * token_info[4]) * token['financial_results'], 2)
      user_portfolio[token_info[2]] = token
      token = {}
    print(user_portfolio)
    return user_portfolio