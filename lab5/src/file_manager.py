from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QListWidget, QPushButton, QWidget, QMessageBox, QTextEdit, QLineEdit, QCheckBox, QSpinBox

from src.db_interactions import DatabaseConnection

from cryptography.fernet import Fernet
import hashlib
import zipfile
import pyminizip

from datetime import datetime
import os

def get_archive_password(db_connection, filename):
    cursor = db_connection.cursor
    cursor.execute("""
                   SELECT archive_password FROM files_lab5 WHERE filename = %s
                   """, (filename, ))
    stored_pass = cursor.fetchone()[0]
    
    return stored_pass

def set_archive_password(db_connection, file_id, new_password):
    cursor = db_connection.cursor
    try:
        cursor.execute("""
                        UPDATE files_lab5
                        SET archive_password = %s
                        WHERE filename = %s
                    """, (new_password, file_id,))
        db_connection.conn.commit()
    except Exception as e:
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании файла: {e}")
        return

def create_password_protected_zip(filename, db_connection, username):
    """
    Создаёт защищённый паролем ZIP-архив из файла с указанным именем.

    :param filename: Имя файла, который нужно заархивировать.
    :param password: Пароль для защиты архива.
    :param compress_level: Уровень компрессии (от 1 до 9, где 9 - максимальная компрессия).
    """
    input_file_path = f'lab5/tmp/{filename}.secret'
    output_zip_path = f'lab5/files/{filename}.zip'
    compress_level=9
    password = username
    try:
        pyminizip.compress(
            input_file_path,
            None,
            output_zip_path,
            password,
            compress_level
        )
        print(f"Архив {output_zip_path} успешно создан.")
    except Exception as e:
        print(f"Произошла ошибка при создании архива: {e}")

    set_archive_password(db_connection, filename, username)

def unzip_protected(filename, out_dir, db_connection):
    input_file_path = f'lab5/files/{filename}.zip'
    password = get_archive_password(db_connection, filename)
    pyminizip.uncompress(input_file_path, password, out_dir, 1)


def hash_modification_time(filepath):
    """
    Вычисляет хэш времени модификации файла.
    """
    try:
        mtime = os.path.getmtime(filepath)  # Получаем время модификации файла
        mtime_str = str(mtime).encode()  # Преобразуем в строку и кодируем в байты
        return hashlib.sha256(mtime_str).hexdigest()  # Возвращаем хэш
    except Exception as e:
        print(f"Ошибка при вычислении хэша времени модификации файла: {e}")
        return None

def verify_modification_time_hash(db_connection, filename, filepath):
    """
    Проверяет, совпадает ли хэш времени модификации файла с сохраненным в базе данных.
    """
    current_hash = hash_modification_time(filepath)
    if not current_hash:
        return False

    cursor = db_connection.cursor
    cursor.execute("SELECT file_hash FROM files_lab5 WHERE filename = %s", (file_id,))
    stored_hash = cursor.fetchone()
    if not stored_hash or current_hash != stored_hash[0]:
        return False
    return True

# Шифрование файла
def encrypt_file(filepath, key):
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(filepath, "wb") as file:
        file.write(encrypted_data)

# Дешифрование файла
def decrypt_file(filepath, key):
    fernet = Fernet(key)
    with open(filepath, "rb") as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')

# Изменение расширение файла
def change_file_extension(filepath, new_extension):
    """Меняет расширение файла."""
    # Проверяем существование файла
    print(filepath)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Файл {filepath} не найден!")

    # Формируем новый путь с измененным расширением
    base = os.path.splitext(filepath)[0]
    new_filepath = f"{base}{new_extension}"
  
    # Переименовываем файл
    os.rename(filepath, new_filepath)
    return new_filepath

# Загрузка ключа
def load_key():
    with open("lab4/secret.key", "rb") as key_file:
        return key_file.read()

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
        
        self.delete_button = QPushButton("Удалить файл", self)
        self.delete_button.clicked.connect(self.delete_file)
        layout.addWidget(self.delete_button)
        
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
            FROM files_lab5 f
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

        # Проверяем наличие файла в базе данных
        cursor = self.db_connection.cursor
        cursor.execute("SELECT file_id, archive_password FROM files_lab5 WHERE filename = %s", (filename,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден в базе данных!")
            return

        file_id, archive_password = result

        # Проверка прав на чтение
        if not self.check_permission("read", filename):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на чтение этого файла.")
            return

        try:
            # Шаг 1: Разархивация файла
            input_zip_path = f"lab5/files/{filename}.zip"
            temp_dir = "lab5/tmp/"
            os.makedirs(temp_dir, exist_ok=True)
            temp_filepath = os.path.join(temp_dir, f"{filename}.secret")

            print(f"Разархивация: {input_zip_path} -> {temp_dir}")
            unzip_protected(filename, temp_dir, self.db_connection)
            print(os.path.list('lab5/files/'))
            # print(os.path.realpath())
            # Проверяем, был ли успешно создан временный файл
            if not os.path.exists(temp_filepath):
                raise FileNotFoundError(f"Файл {temp_filepath} не найден после разархивации.")

            # Шаг 2: Проверяем хэш времени модификации
            print(f"Проверка хэша времени модификации для файла: {temp_filepath}")
            if not verify_modification_time_hash(self.db_connection, filename, temp_filepath):
                QMessageBox.critical(self, "Ошибка", "Целостность файла нарушена!")
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                return

            # Шаг 3: Дешифруем файл
            print(f"Дешифрование файла: {temp_filepath}")
            key = load_key()
            decrypted_data = decrypt_file(temp_filepath, key)
            if decrypted_data is None:
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
                return

            # Шаг 4: Открытие окна для чтения
            print(f"Открытие окна для чтения: {filename}")
            self.file_read_window = FileReadWindow(filename, decrypted_data)
            self.file_read_window.show()

            # Удаление временного файла
            print(f"Удаление временного файла: {temp_filepath}")
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при открытии файла: {e}")



    def edit_file(self):
        """Открытие файла для редактирования."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл!")
            return

        # Получаем имя файла из списка
        filename = selected_item.text()
        filepath = f"lab4/files/{filename}.secret"

        # Запрашиваем file_id из таблицы files по имени файла
        cursor = self.db_connection.cursor
        cursor.execute("SELECT file_id FROM files_lab5 WHERE filename = %s", (filename,))
        result = cursor.fetchone()
        if not result:
            QMessageBox.warning(self, "Ошибка", f"Файл {filename} не найден в базе данных!")
            return

        file_id = result[0]

        # Проверка прав на редактирование
        if not self.check_permission("edit", filename):
            QMessageBox.warning(self, "Ошибка", "У вас нет прав на редактирование этого файла.")
            return

        # Изменяем расширение файла для работы
        temp_filepath = change_file_extension(filepath, ".txt")

        # Проверяем хэш времени модификации
        if not verify_modification_time_hash(self.db_connection, file_id, temp_filepath):
            QMessageBox.critical(self, "Ошибка", "Целостность файла нарушена!")
            change_file_extension(temp_filepath, ".secret")
            return

        # Дешифруем файл
        key = load_key()
        decrypted_data = decrypt_file(temp_filepath, key)
        if decrypted_data is None:
            change_file_extension(temp_filepath, ".secret")
            return

        # Открытие окна для редактирования
        self.file_edit_window = FileEditWindow(filename, decrypted_data, self.db_connection)
        self.file_edit_window.show()

        # Восстанавливаем расширение
        change_file_extension(temp_filepath, ".secret")

    def check_permission(self, action, filename):
        """Проверка прав пользователя на файл."""

        cursor = self.db_connection.cursor
        cursor.execute("SELECT security_level FROM files_lab5 WHERE filename = %s", (filename, ))
        file_sl = cursor.fetchone()[0]
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
    
    def check_create_files_permission(self):
        """Проверяет, есть ли у пользователя право на создание файлов."""
        cursor = self.db_connection.cursor
        cursor.execute("SELECT can_create FROM user_permissions WHERE user_id = %s", (self.user_id,))
        result = cursor.fetchone()
        return result and result[0] 

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

    def delete_file(self):
        """Удаление файла и связанных записей из базы данных."""
        selected_item = self.file_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Ошибка", "Выберите файл для удаления!")
            return

        # Получаем имя файла из списка
        filename = selected_item.text()

        # Проверяем наличие файла
        filepath = f"lab4/files/{filename}.secret"
        if not os.path.exists(filepath):
            QMessageBox.warning(self, "Ошибка", f"Файл '{filename}' не существует!")

        # Подтверждение удаления
        confirm = QMessageBox.question(self, "Подтверждение", f"Вы действительно хотите удалить файл '{filename}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirm == QMessageBox.StandardButton.No:
            return

        # Удаляем файл
        try:
            os.remove(filepath)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить файл: {e}")
            

        # Удаляем запись из таблицы files_lab5
        cursor = self.db_connection.cursor
        cursor.execute("DELETE FROM files_lab5 WHERE filename = %s", (filename,))
        self.db_connection.conn.commit()

        # Обновляем список файлов
        self.load_files()

        QMessageBox.information(self, "Успех", f"Файл '{filename}' успешно удален!")

class FileEditWindow(QMainWindow):
    def __init__(self, filename, file_content, db_connection):
        super().__init__()
        self.filename = filename
        self.file_content = file_content
        self.db_connection = db_connection
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
            # Сохранение зашифрованного файла
            filepath = f"lab4/files/{self.filename}.secret"
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(self.text_edit.toPlainText())

            # Шифруем данные
            key = load_key()
            encrypted_data = encrypt_file(filepath, key)
            
            # Генерация хэша времени изменения
            modification_time_hash = hash_modification_time(filepath)

            # Вставка информации о файле в базу данных
            cursor = self.db_connection.cursor
            cursor.execute(
                """
                UPDATE files_lab5
                SET file_hash = %s
                WHERE filename = %s
                """,
                (modification_time_hash, self.filename, ),
            )
            self.db_connection.conn.commit()

            QMessageBox.information(self, "Успех", "Файл успешно изменен!")
            self.close_and_return_to_parent()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании файла: {e}")
        
    def close_and_return_to_parent(self):
        self.close()
    
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
                cursor.execute("SELECT file_id FROM files_lab5 WHERE filename = %s", (input_value,))
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
            # Шаг 1: Сохранение зашифрованного файла
            tmp_dir = "lab5/tmp"
            os.makedirs(tmp_dir, exist_ok=True)
            filepath = os.path.join(tmp_dir, f"{filename}.secret")

            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(file_content)

            # Шаг 2: Шифруем файл
            key = load_key()  # Загружаем ключ шифрования
            encrypt_file(filepath, key)  # Шифруем файл на месте

            # Шаг 3: Генерация хэша времени изменения
            modification_time_hash = hash_modification_time(filepath)

            # Шаг 4: Создание защищённого ZIP-архива
            create_password_protected_zip(filename, self.db_connection, self.parent.username)

            # Шаг 5: Вставка информации о файле в базу данных
            cursor = self.db_connection.cursor
            cursor.execute(
                """
                INSERT INTO files_lab5 (filename, security_level, file_hash, archive_password)
                VALUES (%s, %s, %s, %s);
                """,
                (filename, security_level, modification_time_hash, self.parent.username),
            )
            self.db_connection.conn.commit()

            # Очистка временного файла
            print(filepath)
            if os.path.exists(filepath):
                os.remove(filepath)

            QMessageBox.information(self, "Успех", "Файл успешно создан и помещён в архив!")
            self.close_and_return_to_parent()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при создании файла: {e}")

    def close_and_return_to_parent(self):
        self.close()
        self.parent.load_files()  # Обновление списка файлов после создания нового