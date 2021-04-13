import sqlite3


from settings import local_settings as ls


class Database:
    def sql_query_execute(self, query, args=None):
        with sqlite3.connect(ls.PATH_TO_DB) as connection:
            cursor = connection.cursor()
            try:
                if args:
                    cursor.execute(query, args)
                else:
                    cursor.execute(query)
            except sqlite3.Error as e:
                print(e)
                return None
            result = cursor.fetchall()
            return result
