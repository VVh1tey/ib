from PyQt6.QtWidgets import QMainWindow, QLabel
from src.utils import hash_password

class DeviceCheckWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Device Check")
        self.setGeometry(300, 300, 400, 200)

        self.status_label = QLabel(self)
        self.status_label.setGeometry(50, 50, 300, 50)

        uuid_hash = self.get_uuid_hash()
        if self.check_device(uuid_hash):
            self.status_label.setText("Device authorized. Access granted.")
        else:
            self.status_label.setText("Unauthorized device. Access denied.")

    def get_uuid_hash(self):
        import os
        uuid_value = str(os.getlogin())
        return hash_password(uuid_value, hash_password(uuid_value, b"salt"))

    def check_device(self, uuid_hash):
        result = self.db_connection.validate_device(uuid_hash)
        return result is not None
