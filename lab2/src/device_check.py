from PyQt6.QtWidgets import QMainWindow, QLabel
from src.utils import hash_password

class DeviceCheckWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.__pc_id = self.get_uuid()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Device Check")
        self.setGeometry(300, 300, 400, 200)

        self.status_label = QLabel(self)
        self.status_label.setGeometry(50, 50, 300, 50)

        if self.check_device():
            self.status_label.setText("Устройство авторизовано.")
        else:
            self.status_label.setText("Устройство не авторизовано. Доступ запрещен.")

    def check_device(self):
        result = self.db_connection.validate_device(hex(int(self.__pc_id)))
        return result is not None
    
    @staticmethod
    def get_uuid():
        import uuid
        try:
            return str(uuid.getnode())
        except Exception as e:
            print(f"Ошибка при получении UUID: {e}")
            return None