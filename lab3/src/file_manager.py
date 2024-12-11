from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QListWidget, QPushButton, QWidget, QMessageBox
from src.db_interactions import DatabaseConnection


class FileManagerWindow(QMainWindow):
    def __init__(self, db_connection, user_id, username):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Управление файлами")
        self.setGeometry(300, 300, 600, 400)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Компоновка
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Логин пользователя
        self.user_label = QLabel(f"Вы вошли как: {self.username}", self)
        layout.addWidget(self.user_label)

        # Список файлов
        self.file_list = QListWidget(self)
        layout.addWidget(self.file_list)

        # Кнопки для работы с файлами
        self.read_button = QPushButton("Открыть файл", self)
        self.read_button.clicked.connect(self.open_file)
        layout.addWidget(self.read_button)

        self.edit_button = QPushButton("Редактировать файл", self)
        self.edit_button.clicked.connect(self.edit_file)
        layout.addWidget(self.edit_button)

        # Загрузка доступных файлов
        self.load_files()

    # def load_files(self):
    #     """Загружает список доступных файлов для пользователя."""
    #     cursor = self.db_connection.cursor
    #     cursor.execute("""
    #         SELECT f.fileid, f.filename 
    #         FROM files f
    #         JOIN permissions p ON f.fileid = p.file_id
    #         WHERE p.user_id = %s AND (p.can_read OR p.can_edit OR p.can_copy)
    #     """, (self.user_id,))
    #     files = cursor.fetchall()

    #     # Очистка списка и добавление файлов
    #     self.file_list.clear()
    #     for file_id, filename in files:
    #         self.file_list.addItem(f"{file_id}: {filename}")
    def load_files(self):
        self.file_list.addItem('123')

    def open_file(self):
        """Открытие файла для чтения."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        filename = selected_item.text()
        file_id = self.db_connection.get_fileid(filename)
        
        if not self.check_permission(file_id, "read"):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на чтение этого файла.")
            return

        QMessageBox.information(self, "Открытие файла", f"Файл {filename} успешно открыт!")

    def edit_file(self):
        """Открытие файла для редактирования."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        file_id, filename = self.parse_selected_item(selected_item.text())
        if not self.check_permission(file_id, "edit"):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на редактирование этого файла.")
            return

        QMessageBox.information(self, "Редактирование файла", f"Файл {filename} открыт для редактирования!")

    def copy_file(self):
        """Копирование файла."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        file_id, filename = self.parse_selected_item(selected_item.text())
        if not self.check_permission(file_id, "copy"):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на копирование этого файла.")
            return

        QMessageBox.information(self, "Копирование файла", f"Файл {filename} скопирован!")

    def check_permission(self, file_id, action):
        """Проверка прав пользователя на файл."""
        cursor = self.db_connection.cursor
        if action == "read":
            cursor.execute("SELECT can_read FROM permissions WHERE user_id = %s AND file_id = %s", (self.user_id, file_id))
        elif action == "edit":
            cursor.execute("SELECT can_edit FROM permissions WHERE user_id = %s AND file_id = %s", (self.user_id, file_id))
        elif action == "copy":
            cursor.execute("SELECT can_copy FROM permissions WHERE user_id = %s AND file_id = %s", (self.user_id, file_id))

        result = cursor.fetchone()
        return result and result[0]
