from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QLabel, QMessageBox
from src.db_interactions import DatabaseConnection, Credentials, User
from src.utils import validate_login, validate_password

class RegistrationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.setGeometry(300, 300, 600, 500)  # Увеличиваем размер окна

        creds = Credentials()
        self.db_conn_write = DatabaseConnection(cfg=creds.get_write())
        self.db_conn_read = DatabaseConnection(cfg=creds.get_read())
        # Поля для логина
        self.login_label = QLabel("Логин (4 цифры):", self)
        self.login_label.move(50, 20)
        self.login_input = QLineEdit(self)
        self.login_input.setFixedSize(500, 30)  # Увеличиваем размер поля
        self.login_input.move(50, 50)

        # Поля для пароля
        self.password_label = QLabel("Пароль (6 символов):", self)
        self.password_label.move(50, 90)
        self.password_input = QLineEdit(self)
        self.password_input.setFixedSize(500, 30)
        self.password_input.move(50, 120)

        # Поля для email
        self.email_label = QLabel("Email:", self)
        self.email_label.move(50, 150)
        self.email_input = QLineEdit(self)
        self.email_input.setFixedSize(500, 30)
        self.email_input.move(50, 180)

        # Поля для имени
        self.name_label = QLabel("Имя:", self)
        self.name_label.move(50, 210)
        self.name_input = QLineEdit(self)
        self.name_input.setFixedSize(500, 30)
        self.name_input.move(50, 240)

        # Поля для фамилии (опционально)
        self.last_name_label = QLabel("Фамилия (опционально):", self)
        self.last_name_label.move(50, 270)
        self.last_name_input = QLineEdit(self)
        self.last_name_input.setFixedSize(500, 30)
        self.last_name_input.move(50, 300)

        # Поля для отчества (опционально)
        self.second_name_label = QLabel("Отчество (опционально):", self)
        self.second_name_label.move(50, 330)
        self.second_name_input = QLineEdit(self)
        self.second_name_input.setFixedSize(500, 30)
        self.second_name_input.move(50, 360)

        # Поля для адреса (опционально)
        self.address_label = QLabel("Адрес (опционально):", self)
        self.address_label.move(50, 390)
        self.address_input = QLineEdit(self)
        self.address_input.setFixedSize(500, 30)
        self.address_input.move(50, 420)

        # Кнопка регистрации
        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setFixedSize(200, 40)  # Увеличиваем размер кнопки
        self.register_button.move(200, 460)
        self.register_button.clicked.connect(self.handle_registration)

    def handle_registration(self):
        # Считываем данные из полей
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        email = self.email_input.text().strip()
        first_name = self.name_input.text().strip()
        last_name = self.last_name_input.text().strip() or None
        second_name = self.second_name_input.text().strip() or None
        address = self.address_input.text().strip() or None

        
        # print(f'l = {login}, p = {password}, e = {email}, fn = {first_name}, ln = {last_name}, sn = {second_name}, a = {address}')
        
        # Проверка логина и пароля
        if not validate_login(login):
            QMessageBox.warning(self, "Ошибка", "Некорректный логин (только 4 цифры).")
            return

        if User.check_user_existance(self.db_conn_read, login):
            QMessageBox.warning(self, "Ошибка", "Такой логин уже существует!")
            return
        
        if not validate_password(password):
            QMessageBox.warning(self, "Ошибка", "Некорректный пароль.")
            return

        # Создаем сущность пользователя
        user = User(
            login=login,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name,
            second_name=second_name,
            address=address
        )

        try:
            # Сохраняем пользователя через класс User
            user.save(self.db_conn_write)
            QMessageBox.information(self, "Успех", "Вы успешно зарегистрировались!")
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при регистрации: {e}")
