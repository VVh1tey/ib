from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QPixmap
from src.utils import check_password, generate_captcha

class LoginWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.failed_attempts = 0
        self.captcha_text = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Login")
        self.setGeometry(300, 300, 400, 400)

        self.login_label = QLabel("Login:", self)
        self.login_label.move(50, 50)
        self.login_input = QLineEdit(self)
        self.login_input.setGeometry(150, 50, 200, 30)

        self.password_label = QLabel("Password:", self)
        self.password_label.move(50, 100)
        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(150, 100, 200, 30)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.captcha_label = QLabel(self)
        self.captcha_label.setGeometry(50, 200, 200, 80)

        self.captcha_input = QLineEdit(self)
        self.captcha_input.setGeometry(150, 300, 200, 30)
        self.captcha_input.setPlaceholderText("Enter Captcha")

        self.login_button = QPushButton("Login", self)
        self.login_button.setGeometry(150, 350, 100, 40)
        self.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if self.failed_attempts >= 3:
            if not self.captcha_text or self.captcha_input.text() != self.captcha_text:
                QMessageBox.warning(self, "Captcha Error", "Invalid captcha!")
                return

        result = self.db_connection.get_user_credentials(login)

        if result:
            password_hash, salt = result
            if check_password(password, password_hash):
                QMessageBox.information(self, "Success", "Login successful!")
                self.close()
            else:
                self.handle_failed_attempt()
        else:
            self.handle_failed_attempt()

    def handle_failed_attempt(self):
        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.generate_and_show_captcha()
        QMessageBox.warning(self, "Error", "Invalid login or password!")

    def generate_and_show_captcha(self):
        self.captcha_text = generate_captcha()
        self.captcha_label.setPixmap(QPixmap("captcha.png"))
