import psycopg2

class DatabaseConnection:
    def __init__(self, config):
        self.conn = psycopg2.connect(**config)
        self.cursor = self.conn.cursor()

    def get_user_credentials(self, login):
        self.cursor.execute(
            "SELECT password_hash, salt FROM users_credentials_lab2 WHERE login = %s", 
            (login,)
        )
        return self.cursor.fetchone()

    def validate_device(self, uuid_hash):
        self.cursor.execute("SELECT * FROM valid_pcs WHERE uuid_hash = %s", (uuid_hash,))
        return self.cursor.fetchone()

    def get_userid(self, login):
        self.cursor.execute("SELECT users.userid FROM users JOIN users_credentials_lab2 uc ON uc.user_creds_id = users.user_creds_id WHERE uc.login = %s",
                            (login,))
        
        return self.cursor.fetchone()
    
    def get_fileid(self, filename):
        self.cursor.execute("SELECT file_id FROM files WHERE files.filename = %s", (filename, ))
        
        return self.cursor.fetchone()
    
    def close(self):
        self.cursor.close()
        self.conn.close()
        
    def add_new_file(self, file_id, filename, security_level):
        try: 
            self.cursor_execute("""
                                INSERT INTO files VALUES
                                (%s, %s, %s);
                                """, (file_id, filename, security_level))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        

class User:
    def __init__(self, login="", password="", email="", first_name="", last_name="", second_name="", address="", password_hash="", salt=""):
        self.login = login
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.second_name = second_name
        self.address = address    
        self.password_hash = password_hash
        self.salt = salt
        
    @staticmethod
    def check_user_existance(db_connection, login):
        cursor = db_connection.cursor
        cursor.execute("SELECT * FROM users_credentials_lab2 WHERE login = %s", (login,))
        return cursor.fetchone() is not None

    def save(self, db_connection):
        cursor = db_connection.cursor
        try:
            # Сохраняем учетные данные
            cursor.execute(
                "INSERT INTO users_credentials_lab2 (login, password_hash, salt) VALUES (%s, %s, %s) RETURNING user_creds_id",
                (self.login, self.password_hash, self.salt)
            )
            user_creds_id = cursor.fetchone()[0]

            # Сохраняем информацию о пользователе
            cursor.execute(
                "INSERT INTO user_info (email, first_name, last_name, second_name, adress) VALUES (%s, %s, %s, %s, %s) RETURNING user_info_id",
                (self.email, self.first_name, self.last_name, self.second_name, self.address)
            )
            user_info_id = cursor.fetchone()[0]

            # Сохраняем запись в таблице users
            cursor.execute(
                "INSERT INTO users (user_creds_id, user_info_id) VALUES (%s, %s)",
                (user_creds_id, user_info_id)
            )

            db_connection.conn.commit()
        except Exception as e:
            db_connection.conn.rollback()
            raise e
