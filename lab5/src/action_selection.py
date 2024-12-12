from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
from src.login import LoginWindow
from src.registration import RegistrationWindow


class ActionSelectionWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.setWindowTitle("Выберите действие")
        self.setGeometry(300, 300, 400, 200)

        self.db_connection = db_connection

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Кнопка логина
        login_button = QPushButton("Логин", self)
        login_button.setFixedSize(200, 50)
        login_button.clicked.connect(self.open_login_window)
        layout.addWidget(login_button)

        # Кнопка регистрации
        register_button = QPushButton("Регистрация", self)
        register_button.setFixedSize(200, 50)
        register_button.clicked.connect(self.open_registration_window)
        layout.addWidget(register_button)

    def open_login_window(self):
        """Открывает окно логина и передаёт в него ссылку на главное меню."""
        self.login_window = LoginWindow(self.db_connection, self)
        self.login_window.show()
        self.hide()

    def open_registration_window(self):
        """Открывает окно регистрации."""
        self.registration_window = RegistrationWindow(self.db_connection, self)
        self.registration_window.show()
        self.hide()
