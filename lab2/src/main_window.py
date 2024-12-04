from PyQt6.QtWidgets import QMainWindow, QLabel

class MainApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Main Application")
        self.setGeometry(300, 300, 500, 400)
        self.label = QLabel("Welcome to the application!", self)
        self.label.setGeometry(50, 50, 400, 50)