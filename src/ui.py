from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog, QLineEdit

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Window')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        
        self.registration_button = QPushButton('Register')
        self.registration_button.clicked.connect(self.open_registration_window)
        layout.addWidget(self.registration_button)
        
        self.login_button = QPushButton('Login')
        self.login_button.clicked.connect(self.open_login_window)
        layout.addWidget(self.login_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_registration_window(self):
        self.registration_window = RegistrationWindow()
        self.registration_window.show()
        
    def open_login_window(self):
        self.login_window = LoginWindow()
        self.login_window.show()

class RegistrationWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Registration')
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton('Register')
        layout.addWidget(self.register_button)

        self.setLayout(layout)
        
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Login')
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()
        
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText('Username')
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText('Password')
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        self.register_button = QPushButton('Login')
        layout.addWidget(self.register_button)

        self.setLayout(layout)