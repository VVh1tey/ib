from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtCore import pyqtSignal


class MainWindow(QMainWindow):
    # Объявляем сигнал, который будет испускаться при вызове logout()
    logout_signal = pyqtSignal()

    def __init__(self, username):
        """
        Окно, отображающее информацию об авторизованном пользователе.
        :param username: Имя пользователя, передается из LoginWindow
        """
        super().__init__()

        self.setWindowTitle("Main Window")
        self.setGeometry(300, 300, 600, 400)

        # Центрируем интерфейс
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Надпись с именем пользователя
        self.user_label = QLabel(f"Вы авторизированы как, {username}", self)
        self.user_label.setStyleSheet("font-size: 18px;")
        layout.addWidget(self.user_label)

        # Пример кнопки для выхода
        self.logout_button = QPushButton("Выйти", self)
        self.logout_button.clicked.connect(self.logout)
        layout.addWidget(self.logout_button)

        self.setCentralWidget(central_widget)

    def logout(self):
        """
        Метод для выхода из главного окна при нажатии на 'Выйти'.
        Испускает сигнал 'logout_signal', который может быть обработан наверху.
        """
        self.logout_signal.emit()  # Отправляем сигнал о выходе
        self.close()  # Закрываем главное окно
