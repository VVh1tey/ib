from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def save_key_to_file(file_name, key):
    with open(file_name, 'wb') as key_file:  # Открываем файл в режиме записи (binary)
        key_file.write(key)

if __name__ == "__main__":
    # Генерируем ключ
    key = generate_key()
    
    # Сохраняем ключ в файл
    save_key_to_file('lab4/secret.key', key)

    print("Ключ сохранён в файл 'secret.key'")
