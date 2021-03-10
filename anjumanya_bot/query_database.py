import sqlite3

from local_settings import NAME_DB


query_create_users = '''
CREATE TABLE IF NOT EXISTS users(
   user_id INT PRIMARY KEY,
   username TEXT,
   firstname TEXT,
   lastname TEXT
   );
'''

query_create_exercises = '''
CREATE TABLE IF NOT EXISTS exercises(
   id INT PRIMARY KEY,
   name TEXT
   );
'''

query_create_results_training = '''
CREATE TABLE IF NOT EXISTS results_training(
   id INT PRIMARY KEY,
   user_id INT,
   exercise_id INT,
   sets FLOAT,
   repetition FLOAT,
   date_insert INT,
   FOREIGN KEY (user_id) 
      REFERENCES users (user_id) 
         ON DELETE CASCADE 
         ON UPDATE NO ACTION,
   FOREIGN KEY (exercise_id) 
      REFERENCES exercises (id) 
         ON DELETE CASCADE 
         ON UPDATE NO ACTION
   );
'''

def sql_query(query):
    with sqlite3.connect(NAME_DB) as connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query)
        except sqlite3.Error as e:
            print(e)
            return None
        result = cursor.fetchall()
        return result


def create_db():
    sql_query(query_create_users)
    sql_query(query_create_exercises)
    sql_query(query_create_results_training)

