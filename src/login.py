from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QLabel, QMessageBox
from src.db_interactions import DatabaseConnection, Credentials, User

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход")
        self.setGeometry(300, 300, 400, 200)

        self.attempts = 3
        creds = Credentials()
        self.db_connection = DatabaseConnection(cfg=creds.get_read())

        self.login_label = QLabel("Логин:", self)
        self.login_label.move(50, 20)
        self.login_input = QLineEdit(self)
        self.login_input.move(50, 50)

        self.password_label = QLabel("Пароль:", self)
        self.password_label.move(50, 90)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.move(50, 120)

        self.login_button = QPushButton("Войти", self)
        self.login_button.move(50, 160)
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        # Создаем сущность пользователя только с логином
        user = User(login=login)

        if not user.login:
            QMessageBox.warning(self, "Ошибка", "Логин должен быть указан.")
            return

        if self.db_connection.validate_user(user.login, password):
            QMessageBox.information(self, "Успех", f"Здравствуйте, {user.login}, вы успешно вошли!")
            self.close()
        else:
            self.attempts -= 1
            if self.attempts > 0:
                QMessageBox.warning(self, "Ошибка", f"Неверные данные. Осталось попыток: {self.attempts}.")
            else:
                QMessageBox.critical(self, "Ошибка", "Все попытки исчерпаны!")
                self.close()
