# region imports
import psycopg2 as pg
import configparser as cfgp


# endregion

# region Data Models

class Credentials:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Credentials, cls).__new__(cls)

            cfg = cfgp.ConfigParser(allow_no_value=False, delimiters='=')
            cfg.read('db_creds.ini', encoding='utf-8')
            
            cls.__read = dict(cfg['read'])
            cls.__write = dict(cfg['write'])

        return cls._instance

    def get_read(self):
        # print(self.__read)
        return self.__read

    def get_write(self):
        # print(self.__write)
        return self.__write


class User:
    def __init__(self, login="", password="", email="", first_name="", last_name="", second_name="", address=""):
        self.login = login
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.second_name = second_name
        self.address = address

    def save(self, db_connection):
        """
        Сохраняет пользователя в базу данных.
        """
        try:
            cursor = db_connection.cursor
            
            # Сначала сохраняем учетные данные
            cursor.execute('''
                INSERT INTO users_credentials(login, password)
                VALUES (%s, %s)
                RETURNING user_creds_id;
            ''', (self.login, self.password))
            user_creds_id = cursor.fetchone()[0]

            # Затем сохраняем информацию о пользователе
            cursor.execute('''
                INSERT INTO user_info(email, first_name, last_name, second_name, adress)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING user_info_id;
            ''', (self.email, self.first_name, self.last_name, self.second_name, self.address))
            user_info_id = cursor.fetchone()[0]

            # Сохраняем общую запись в Users
            cursor.execute('''
                INSERT INTO users (user_creds_id, user_info_id)
                VALUES (%s, %s);
            ''', (user_creds_id, user_info_id))

            db_connection.conn.commit()
            print("Пользователь успешно сохранен.")
        except Exception as e:
            try:
                db_connection.conn.rollback()
                db_connection.conn.close()
                print(f"Ошибка при сохранении пользователя: {e}")
            except Exception as e2:
                db_connection.conn.close()
                print(f"Ошибка при откате транзакцииЖ {e2}")
                raise e2
            raise e
    
    @staticmethod
    def check_user_existance(db_connection, login):
        try:
            cursor = db_connection.cursor

            cursor.execute('''
                SELECT user_creds_id FROM users_credentials
                WHERE login = %s
            ''', (login,))
            user_creds_id = cursor.fetchone()
            if user_creds_id is not None:
                return True
            else:
                return False
        except Exception as e:
            print(f"Ошибка при поиске пользователя: {e}")
            raise e

class DatabaseConnection:
    def __init__(self, cfg: dict):
        try:
            self.conn = pg.connect(
                host=str(cfg['host']),
                port=int(cfg['port']),
                user=str(cfg['user']),
                password=str(cfg['password']),
                dbname=str(cfg['database']),
                connect_timeout=100
            )
            self.cursor = self.conn.cursor()
            # print(f"Подключение для {cfg['user']} успешно!")
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            self.conn = None
            self.cursor = None

    def find_user(self, login):
        """
        Ищет пользователя по логину.
        Возвращает None, если пользователь не найден.
        """
        try:
            self.cursor.execute('''
                SELECT uc.login, uc.password, ui.email, ui.first_name, ui.last_name, ui.second_name
                FROM Users_credentials AS uc
                JOIN Users AS u ON uc.user_creds_id = u.user_creds_id
                JOIN User_info AS ui ON ui.user_info_id = u.user_info_id
                WHERE uc.login = %s;
            ''', (login,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"Ошибка при поиске пользователя: {e}")
            return None

    def validate_user(self, login, password):
        """
        Проверяет, существует ли пользователь с данным логином и паролем.
        """
        try:
            user_data = self.find_user(login)
            if not user_data:
                return False

            stored_password = user_data[1]  # Хэш пароля из базы данных
            return password == stored_password
        except Exception as e:
            print(f"Ошибка при проверке пользователя: {e}")
            return False

    def __del__(self):
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception as e:
            print(f"Ошибка при закрытии подключения: {e}")


class Device:
    def __init__(self, creds):
        self.__pc_id = self.get_uuid()
        self.creds = creds
        self.continue_actions = self.__validate_pc()

    @staticmethod
    def get_uuid():
        import uuid
        try:
            return str(uuid.getnode())
        except Exception as e:
            print(f"Ошибка при получении UUID: {e}")
            return None

    def __validate_pc(self):
        """
        Проверяет, разрешено ли запускать программу на данном устройстве.
        """
        try:
            dbc = DatabaseConnection(cfg=self.creds)
            dbc.cursor.execute('''
                SELECT * FROM Valid_pcs WHERE uuid_hash = %s
            ''', (hex(int(self.__pc_id)), ))
            result = dbc.cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Ошибка при валидации ПК: {e}")
            return None

# endregion
