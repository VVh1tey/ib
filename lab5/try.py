import pyminizip

# Путь к исходному файлу
input_file_path = 'lab5/tmp/lab5file.secret'
# Путь к выходному ZIP-файлу
output_zip_path = 'lab5/files/lab5file.zip'
# Имя файла внутри архива
filename_inside_archive = 'lab5file.secret'
# Пароль для архива
password = '2222'
# Уровень компрессии (значение от 1 до 9, где 9 - максимальная компрессия)
compress_level = 9

# Создаём архив с защитой паролем
pyminizip.compress(
    input_file_path,
    filename_inside_archive,
    output_zip_path,
    password,
    compress_level
)