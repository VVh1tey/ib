from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QPixmap
from src.utils import check_password, generate_captcha
from src.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self, db_connection, main_menu_window):
        super().__init__()
        self.db_connection = db_connection
        self.main_menu_window = main_menu_window  # Ссылка на главное меню
        self.failed_attempts = 0  # Счётчик неудачных попыток
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Логин")
        self.setGeometry(300, 300, 400, 300)

        self.login_label = QLabel("Логин:", self)
        self.login_label.move(50, 50)
        self.login_input = QLineEdit(self)
        self.login_input.setGeometry(150, 50, 200, 30)

        self.password_label = QLabel("Пароль:", self)
        self.password_label.move(50, 100)
        self.password_input = QLineEdit(self)
        self.password_input.setGeometry(150, 100, 200, 30)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Кнопка "Войти"
        self.login_button = QPushButton("Войти", self)
        self.login_button.setGeometry(80, 200, 100, 40)
        self.login_button.clicked.connect(self.handle_login)

        # Кнопка "Назад"
        self.back_button = QPushButton("Назад", self)
        self.back_button.setGeometry(220, 200, 100, 40)
        self.back_button.clicked.connect(self.handle_back)

    def handle_login(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()

        # Проверка логина и пароля
        result = self.db_connection.get_user_credentials(login)
        if result:
            password_hash, salt = result
            if check_password(password, password_hash):
                QMessageBox.information(self, "Успех", "Вы успешно вошли!")
                self.open_main_window(login)
                return
            else:
                self.failed_attempts += 1
        else:
            self.failed_attempts += 1

        # Обработка неудачных попыток
        if self.failed_attempts >= 3:
            self.open_captcha_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль!")

    def open_main_window(self, username):
        """Открыть главное окно после успешного входа."""
        self.main_window = MainWindow(username)
        self.main_window.logout_signal.connect(self.handle_logout)
        self.main_window.show()
        self.close()

    def handle_logout(self):
        """Обработчик выхода из главного окна."""
        self.show()

    def open_captcha_window(self):
        """Открыть окно капчи."""
        self.captcha_window = CaptchaWindow(self)
        self.captcha_window.show()
        self.hide()

    def handle_back(self):
        """Обработчик кнопки 'Назад'. Закрывает окно логина и возвращает в главное меню."""
        self.close()
        self.main_menu_window.show()


class CaptchaWindow(QMainWindow):
    def __init__(self, parent_login_window):
        super().__init__()
        self.parent_login_window = parent_login_window  # Ссылка на окно логина
        self.captcha_text = generate_captcha()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Подтверждение")
        self.setGeometry(300, 300, 400, 300)

        self.info_label = QLabel("Введите текст с изображения:", self)
        self.info_label.move(50, 50)

        self.captcha_label = QLabel(self)
        self.captcha_label.setPixmap(QPixmap("lab2/tmp/captcha.png"))
        self.captcha_label.setGeometry(50, 80, 200, 80)

        self.captcha_input = QLineEdit(self)
        self.captcha_input.setGeometry(50, 180, 300, 30)
        self.captcha_input.setPlaceholderText("Введите капчу")

        self.submit_button = QPushButton("Подтвердить", self)
        self.submit_button.setGeometry(150, 230, 100, 40)
        self.submit_button.clicked.connect(self.handle_captcha_submission)

    def handle_captcha_submission(self):
        if self.captcha_input.text().strip() == self.captcha_text:
            QMessageBox.information(self, "Успех", "Капча введена верно!")
            self.close()
            self.parent_login_window.failed_attempts = 0  # Сбрасываем счётчик
            self.parent_login_window.show()  # Возвращаем окно логина
        else:
            QMessageBox.warning(self, "Ошибка", "Неверная капча!")
