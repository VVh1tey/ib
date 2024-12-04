import psycopg2

class DatabaseConnection:
    def __init__(self, config):
        self.conn = psycopg2.connect(**config)
        self.cursor = self.conn.cursor()

    def get_user_credentials(self, login):
        self.cursor.execute(
            "SELECT password_hash, salt FROM users_credentionals WHERE login = %s", 
            (login,)
        )
        return self.cursor.fetchone()

    def validate_device(self, uuid_hash):
        self.cursor.execute("SELECT * FROM valid_pcs WHERE uuid_hash = %s", (uuid_hash,))
        return self.cursor.fetchone()

    def close(self):
        self.cursor.close()
        self.conn.close()