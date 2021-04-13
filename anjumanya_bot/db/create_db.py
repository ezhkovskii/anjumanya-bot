import sqlite3

create_user = """CREATE TABLE IF NOT EXISTS users(
   user_id INTEGER PRIMARY KEY,
   username TEXT,
   name TEXT
   );
"""

create_data_training = """
CREATE TABLE IF NOT EXISTS data_training(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   user_id INTEGER,
   exercise TEXT,
   type_ex TEXT,
   sets INTEGER,
   repetition INTEGER,
   duration_training INTEGER,
   date_insert DATE,
   FOREIGN KEY (user_id)
      REFERENCES users (user_id)
         ON DELETE CASCADE
         ON UPDATE NO ACTION
   );
"""


def sql_query_execute(query):
    with sqlite3.connect("anjumanya.db") as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query)
        except sqlite3.Error as e:
            print(e)
            return None
        result = cursor.fetchall()
        return result

if __name__ == "__main__":
    tables = (create_user, create_data_training)
    for t in tables:
        if sql_query_execute(t) is None:
            print(f'Команда {t} не выполнилась\n')
