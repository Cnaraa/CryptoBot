import sqlite3

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

def check_in_database(new_token):
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
  return True



def add_new_token(new_token):
  with sqlite3.connect('crypto.db') as connection:
     cursor = connection.cursor()
     cursor.execute("""
        INSERT INTO users_portfolio (id, user_id, token_name, token_amount, total_costs)
        VALUES (NULL, ?, ?, ?, ?)
""", (new_token['user_id'], new_token['token_name'], new_token['token_amount'], new_token['token_price']))
     connection.commit()
  return True