from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QListWidget, QPushButton, QWidget, QMessageBox, QTextEdit, QLineEdit, QCheckBox, QSpinBox
from src.db_interactions import DatabaseConnection
import os

class FileManagerWindow(QMainWindow):
    def __init__(self, db_connection, user_id, username, main_menu_window):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.username = username
        self.main_menu_window = main_menu_window
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
        
        self.manage_roles_button = QPushButton("Управление ролями", self)
        self.manage_roles_button.clicked.connect(self.open_role_management)
        layout.addWidget(self.manage_roles_button)
        
         # Проверка права на редактирование ролей
        if not self.check_edit_roles_permission():
            self.manage_roles_button.setEnabled(False)  # Отключаем кнопку, если права отсутствуют
        
        # Кнопка "Создать файл"
        self.create_button = QPushButton("Создать файл", self)
        self.create_button.clicked.connect(self.create_file)
        layout.addWidget(self.create_button)
        
        # Кнопка "Назад"
        self.back_button = QPushButton("Назад", self)
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.load_files()

    def go_back(self):
        """Возвращает в меню логина."""
        self.close()
        self.main_menu_window.show()

    def load_files(self):
        """Загружает список доступных файлов для пользователя."""
        cursor = self.db_connection.cursor
        cursor.execute("""
                                               SELECT ul.security_level FROM users_levels ul WHERE ul.user_id = %s
                                               """, (self.user_id, ))
        user_permission_level = cursor.fetchall()
        
        cursor.execute("""
            SELECT f.file_id, f.filename, f.security_level 
            FROM files f
            WHERE f.security_level >= %s 
        """, (user_permission_level,))
        files = cursor.fetchall()

        # Очистка списка и добавление файлов
        self.file_list.clear()
        for file_id, filename, security_level  in files:
            self.file_list.addItem(f"{filename}")

    def open_file(self):
        """Открытие файла для чтения."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        # Получаем имя файла из списка
        filename = selected_item.text()

        # Запрашиваем file_id из таблицы files по имени файла
        cursor = self.db_connection.cursor
        cursor.execute("SELECT file_id FROM files WHERE filename = %s", (filename,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден в базе данных!")
            return

        file_id = result[0]

        # Проверка прав на чтение
        if not self.check_permission("read", filename):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на чтение этого файла.")
            return

        # Чтение содержимого файла
        try:
            with open(f'lab3/files/{filename}', "r", encoding="utf-8") as file:
                file_content = file.read()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл {filename}: {e}")
            return

        # Открытие окна для просмотра
        self.file_read_window = FileReadWindow(filename, file_content)
        self.file_read_window.show()

    def create_file(self):
        """Открывает окно для создания нового файла."""
        cursor = self.db_connection.cursor
        cursor.execute("""
                    SELECT ul.security_level FROM users_levels ul WHERE ul.user_id = %s
                    """, (self.username, ))
        user_permission_level = cursor.fetchone()[0]

        if self.check_create_files_permission():
            self.create_file_window = CreateFileWindow(parent=self,
                                                    db_connection=self.db_connection,
                                                    user_id=self.user_id,
                                                    level=user_permission_level)
            self.create_file_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на создание файлов.")
            return

        
    def edit_file(self):
        """Открытие файла для редактирования."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        # Получаем имя файла из списка
        filename = selected_item.text()

        # Запрашиваем file_id из таблицы files по имени файла
        cursor = self.db_connection.cursor
        cursor.execute("SELECT file_id FROM files WHERE filename = %s", (filename,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден в базе данных!")
            return

        file_id = result[0]

        # Проверка прав на редактирование
        if not self.check_permission("edit", filename):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на редактирование этого файла.")
            return

        # Чтение содержимого файла
        try:
            with open(f'lab3/files/{filename}', "r", encoding="utf-8") as file:
                file_content = file.read()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл {filename}: {e}")
            return

        # Открытие окна для редактирования
        self.file_edit_window = FileEditWindow(filename, file_content)
        self.file_edit_window.show()

    def check_permission(self, action, filename):
        """Проверка прав пользователя на файл."""

        cursor = self.db_connection.cursor
        cursor.execute("SELECT security_level FROM files WHERE filename = %s", (filename, ))
        file_sl = cursor.fetchone()[0]
        print(file_sl)
        cursor.execute("SELECT security_level FROM users_levels WHERE user_id = %s", (self.username, ))
        user_sl = cursor.fetchone()[0]
        if action == "read":
            if user_sl <= file_sl:
                cursor.execute("SELECT can_read FROM user_permissions WHERE user_id = %s ", (self.user_id, ))
            else:
                return False
        elif action == "edit":
            if user_sl >= file_sl:
                cursor.execute("SELECT can_edit FROM user_permissions WHERE user_id = %s", (self.user_id, ))
            else:
                return False
        result = cursor.fetchone()
        return result and result[0]

    def open_role_management(self):
        """Открывает окно управления ролями, если у пользователя есть соответствующие права."""
        cursor = self.db_connection.cursor
        cursor.execute("SELECT can_edit_roles FROM user_permissions WHERE user_id = %s", (self.user_id,))
        result = cursor.fetchone()

        if result and result[0]:
            self.role_management_window = RoleManagementWindow(self.db_connection)
            self.role_management_window.show()
        else:
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на управление ролями.")
    
    
    def check_edit_roles_permission(self):
        """Проверяет, есть ли у пользователя право на изменение ролей."""
        cursor = self.db_connection.cursor
        cursor.execute("SELECT can_edit_roles FROM user_permissions WHERE user_id = %s", (self.user_id,))
        result = cursor.fetchone()
        return result and result[0] 

    def check_create_files_permission(self):
        """Проверяет, есть ли у пользователя право на создание файлов."""
        cursor = self.db_connection.cursor
        cursor.execute("SELECT can_create FROM user_permissions WHERE user_id = %s", (self.user_id,))
        result = cursor.fetchone()
        return result and result[0] 


class FileEditWindow(QMainWindow):
    def __init__(self, filename, file_content):
        super().__init__()
        self.filename = filename
        self.file_content = file_content
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Редактирование файла: {self.filename}")
        self.setGeometry(300, 300, 600, 400)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Компоновка
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Виджет текста
        self.text_edit = QTextEdit(self)
        self.text_edit.setPlainText(self.file_content)  # Загружаем содержимое файла
        layout.addWidget(self.text_edit)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.save_file)
        layout.addWidget(self.save_button)

    def save_file(self):
        """Сохраняет изменения в файл."""
        try:
            with open(f'lab3/files/{self.filename}', "w", encoding="utf-8") as file:
                file.write(self.text_edit.toPlainText())
            QMessageBox.information(self, "Успех", f"Файл {self.filename} успешно сохранён!")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении файла: {e}")
    
class FileReadWindow(QMainWindow):
    def __init__(self, filename, file_content):
        super().__init__()
        self.filename = filename
        self.file_content = file_content
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f"Просмотр файла: {self.filename}")
        self.setGeometry(300, 300, 600, 400)

        # Основной виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Компоновка
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Виджет текста
        self.text_display = QTextEdit(self)
        self.text_display.setPlainText(self.file_content)  # Загружаем содержимое файла
        self.text_display.setReadOnly(True)  # Запрещаем редактирование
        layout.addWidget(self.text_display)

        # Кнопка закрытия окна
        self.close_button = QPushButton("Закрыть", self)
        self.close_button.clicked.connect(self.close)
        layout.addWidget(self.close_button)

class CreateFileWindow(QMainWindow):
    def __init__(self, parent=None, db_connection=None, user_id=None, level=None):
        super().__init__()
        self.parent = parent
        self.db_connection = db_connection
        self.user_id = user_id
        self.level = level
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание файла")
        self.setGeometry(300, 300, 600, 400)

        # Центральный виджет
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Главная компоновка
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Поле для ввода содержимого файла
        self.content_textedit = QTextEdit(self)
        content_label = QLabel("Содержание файла:")
        layout.addWidget(content_label)
        layout.addWidget(self.content_textedit)

        # Уровень секретности файла
        self.level_spinbox = QSpinBox(self)
        self.level_spinbox.setRange(1, int(self.level))
        self.level_spinbox.setValue(int(self.level))
        level_label = QLabel("Уровень доступа (1, 2, 3):")
        layout.addWidget(level_label)
        layout.addWidget(self.level_spinbox)

        # Имя файла
        self.filename_lineedit = QLineEdit(self)
        filename_label = QLabel("Имя файла:")
        layout.addWidget(filename_label)
        layout.addWidget(self.filename_lineedit)

        # Кнопки Создать и Назад
        create_button = QPushButton("Создать", self)
        back_button = QPushButton("Назад", self)

        # Событие при нажатии на кнопку "Создать"
        create_button.clicked.connect(self.save_file)

        # Событие при нажатии на кнопку "Назад"
        back_button.clicked.connect(self.close_and_return_to_parent)

        # Компоновка кнопок
        button_layout = QVBoxLayout()
        button_layout.addStretch()  # Центрируем кнопки
        button_layout.addWidget(create_button)
        button_layout.addWidget(back_button)

        # Добавляем компоновку кнопок в главную компоновку
        layout.addLayout(button_layout)


    def save_file(self):
        file_content = self.content_textedit.toPlainText()
        security_level = self.level_spinbox.value()
        filename = self.filename_lineedit.text().strip()

        if not filename or not file_content:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все поля.")
            return

        try:
            cursor = self.db_connection.cursor
            cursor.execute(
                """
                INSERT INTO files (filename, security_level)
                VALUES (%s, %s);
                """,
                (filename, security_level, ),
            )
            self.db_connection.conn.commit()
            
            with open(os.path.join('lab3/files', filename), 'w') as file:
                file.write(file_content)
            QMessageBox.information(self, "Успех", "Файл успешно создан!")
            self.close_and_return_to_parent()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании файла: {e}")

    def close_and_return_to_parent(self):
        self.close()
        self.parent.load_files()  # Обновление списка файлов после создания нового

class RoleManagementWindow(QMainWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Управление правами и уровнями доступа")
        self.setGeometry(300, 300, 600, 400)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Поле для ввода логина пользователя или имени файла
        self.input_label = QLabel("Введите логин пользователя или имя файла:", self)
        layout.addWidget(self.input_label)

        self.input_field = QLineEdit(self)
        layout.addWidget(self.input_field)

        # Поля для новых прав
        self.read_checkbox = QCheckBox("Чтение (can_read)", self)
        layout.addWidget(self.read_checkbox)

        self.edit_checkbox = QCheckBox("Редактирование (can_edit)", self)
        layout.addWidget(self.edit_checkbox)

        self.copy_checkbox = QCheckBox("Копирование (can_copy)", self)
        layout.addWidget(self.copy_checkbox)

        self.edit_roles_checkbox = QCheckBox("Изменение ролей (can_edit_user_roles)", self)
        layout.addWidget(self.edit_roles_checkbox)

        # Поле для уровня доступа
        self.level_label = QLabel("Уровень доступа (1, 2, 3):", self)
        layout.addWidget(self.level_label)

        self.security_level_input = QSpinBox(self)
        self.security_level_input.setRange(1, 3)
        layout.addWidget(self.security_level_input)

        # Кнопка сохранения
        self.save_button = QPushButton("Сохранить", self)
        self.save_button.clicked.connect(self.update_permissions_and_level)
        layout.addWidget(self.save_button)

    def update_permissions_and_level(self):
        """Обновляет права и уровень доступа для пользователя или файла."""
        input_value = self.input_field.text().strip()
        new_security_level = self.security_level_input.value()

        # Проверка наличия ввода
        if not input_value:
            QMessageBox.warning(self, "Ошибка", "Введите логин пользователя или имя файла!")
            return

        # Получение значений прав
        can_read = self.read_checkbox.isChecked()
        can_edit = self.edit_checkbox.isChecked()
        can_copy = self.copy_checkbox.isChecked()
        can_edit_roles = self.edit_roles_checkbox.isChecked()

        cursor = self.db_connection.cursor

        try:
            # Проверка: это пользователь или файл
            user_result = self.db_connection.get_userid(input_value)

            if user_result:
                user_id = user_result[0]

                # Обновление прав пользователя
                cursor.execute("""
                    UPDATE user_permissions
                    SET can_read = %s, can_edit = %s, can_copy = %s, can_edit_roles = %s
                    WHERE user_id = %s
                """, (can_read, can_edit, can_copy, can_edit_roles, user_id))

                # Обновление уровня доступа пользователя
                cursor.execute("""
                    UPDATE users_levels
                    SET security_level = %s
                    WHERE user_id = %s
                """, (new_security_level, user_id))

                self.db_connection.conn.commit()
                QMessageBox.information(self, "Успех", f"Права и уровень доступа пользователя с ID {user_id} обновлены.")
            else:
                # Проверка: это файл
                cursor.execute("SELECT file_id FROM files WHERE filename = %s", (input_value,))
                file_result = cursor.fetchone()

                if file_result:
                    file_id = file_result[0]

                    # Обновление уровня доступа файла
                    cursor.execute("""
                        UPDATE files
                        SET security_level = %s
                        WHERE file_id = %s
                    """, (new_security_level, file_id))

                    self.db_connection.conn.commit()
                    QMessageBox.information(self, "Успех", f"Уровень доступа файла {input_value} обновлен.")
                else:
                    QMessageBox.warning(self, "Ошибка", "Пользователь или файл не найдены!")
        except Exception as e:
            self.db_connection.conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить права или уровень доступа: {e}")

