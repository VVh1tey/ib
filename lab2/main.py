from PyQt6.QtWidgets import QApplication
from src.db_interactions import DatabaseConnection
from src.device_check import DeviceCheckWindow
from src.login import LoginWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Подключение к базе данных
    db_config = {
        "host": "10.147.20.167",
        "port": 5432,
        "user": "a",
        "password": "ab",
        "dbname": "lab_1"
    }
    db_connection = DatabaseConnection(db_config)

    # Проверка устройства
    device_window = DeviceCheckWindow(db_connection)
    device_window.show()

    # Окно логина
    login_window = LoginWindow(db_connection)
    login_window.show()

    sys.exit(app.exec())
