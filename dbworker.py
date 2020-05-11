import sqlite3
import logging
from exceptions import DBException


def get_db_worker():
    return SQLiteWorker('')


class SQLiteWorker:

    def __init__(self, database=None):
        try:
            if database:
                self.connection = sqlite3.connect(database, check_same_thread=False)
            else:
                self.connection = sqlite3.connect(':memory:', check_same_thread=False)
            self.cursor = self.connection.cursor()
            self.create_user_city_table()
        except Exception as ex:
            logging.error(ex)
            raise DBException(ex)

    # Создаем таблице user_city
    def create_user_city_table(self):
        user_city_table_query = '''CREATE TABLE user_city (
            user_id INTEGER PRIMARY KEY,
            city NOT NULL);'''
        with self.connection:
            self.cursor.execute(user_city_table_query)

    # Сохраняем город отправление
    def set_user_src_city(self, user_id, city):
        try:
            with self.connection:
                self.cursor.execute("INSERT OR REPLACE INTO user_city (user_id, city) VALUES (?, ?)", (user_id, city))
        except Exception as ex:
            logging.error(ex)
            raise DBException(ex)

    # Получить город отправление
    def get_user_src_city(self, user_id):
        try:
            with self.connection:
                result = self.cursor.execute('SELECT city FROM user_city WHERE user_id = ?', (user_id,)).fetchall()
                if len(result) > 0:
                    return result[0][0]
        except Exception as ex:
            logging.error(ex)
            raise DBException(ex)

    # Закрываем текущее соединение с БД
    def close(self):
        try:
            self.connection.close()
        except Exception as ex:
            logging.error(ex)
            raise DBException(ex)
