class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

class Device:
    def __init__(self, device_id, user_id):
        self.device_id = device_id
        self.user_id = user_id