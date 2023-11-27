import sqlite3
from check_token import check_token

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
          total_costs DECIMAL(10, 2),
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
        INSERT INTO users_portfolio (id, user_id, token_name, token_amount, total_costs)
        VALUES (NULL, ?, ?, ?, ?)
""", (new_token['user_id'], new_token['token_name'], new_token['token_amount'], (new_token['token_price'] * new_token['token_amount'])))
     connection.commit()
  return True


def check_token_in_portfolio(new_token):
  with sqlite3.connect('crypto.db') as connection:
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM users_portfolio WHERE user_id = (?) and token_name = (?)
""", (new_token['user_id'], new_token['token_name']))
    result = cursor.fetchone()
    if new_token['action'] == 'add':
      if result is None:
        add_new_token(new_token)
      else:
        token_amount = result[3] + new_token['token_amount']
        total_costs = result[4] + (new_token['token_price'] * new_token['token_amount'])
        cursor.execute("""
            UPDATE users_portfolio SET token_amount = (?) WHERE user_id = (?) and token_name = (?)
  """, (token_amount, new_token['user_id'], new_token['token_name']))
        cursor.execute("""
            UPDATE users_portfolio SET total_costs = (?) WHERE user_id = (?) and token_name = (?)
  """, (total_costs, new_token['user_id'], new_token['token_name']))
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
        SELECT token_amount, total_costs FROM users_portfolio WHERE user_id = (?) and token_name = (?)
""", (new_token['user_id'], new_token['token_name']))
    result = cursor.fetchone()
    cursor.execute('''
        UPDATE users_portfolio SET token_amount = (?), total_costs = (?) WHERE user_id = (?) and token_name = (?) 
''', ((result[0] - new_token['token_amount']),
      ((result[1] - new_token['token_amount'] * new_token['token_price'])),
      new_token['user_id'], new_token['token_name']))
    connection.commit()
    cursor.execute('''
        INSERT INTO users_portfolio (id, user_id, token_name, token_amount, total_costs)
        VALUES (NULL, ?, ?, ?, ?)
''', (new_token['user_id'], 'USDT', (new_token['token_amount'] * new_token['token_price']),
      (new_token['token_amount'] * new_token['token_price'])))
    connection.commit()