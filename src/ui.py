from PyQt6.QtWidgets import QMainWindow, QPushButton, QMessageBox
from src.login import LoginWindow
from src.registration import RegistrationWindow

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Добро пожаловать!")
        self.setGeometry(300, 300, 400, 200)

        self.login_button = QPushButton("Логин", self)
        self.login_button.setGeometry(50, 50, 300, 50)
        self.login_button.clicked.connect(self.open_login)

        self.register_button = QPushButton("Регистрация", self)
        self.register_button.setGeometry(50, 120, 300, 50)
        self.register_button.clicked.connect(self.open_registration)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()

    def open_registration(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()