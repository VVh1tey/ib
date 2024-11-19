import psycopg2
from psycopg2 import sql
from models import User

class DatabaseUtils:
    def __init__(self):
        self.connection = psycopg2.connect(
            dbname="your_db_name",
            user="your_user",
            password="your_password",
            host="localhost"
        )
    
    def save_user(self, user):
        with self.connection.cursor() as cursor:
            query = sql.SQL("INSERT INTO users (username, password_hash) VALUES (%s, %s)")
            cursor.execute(query, (user.username, user.password_hash))
            self.connection.commit()

class Validator:
    @staticmethod
    def validate_username(username):
        return len(username) > 3  # Минимальная длина 4 символа

    @staticmethod
    def validate_password(password):
        return len(password) > 6  # Минимальная длина 7 символов