import datetime
import psycopg2 as pg
import hashlib
import configparser as cfgp

cfg = cfgp.ConfigParser(allow_no_value=False, delimiters='=')
cfg.read('db_creds.ini')
d = {}
d = cfg['read']
print(cfg['read'], cfg['write'])
def get_uuid(): 
    import uuid
    try: 
        pc_uuid = str(uuid.getnode()) 
        return pc_uuid 
    except Exception as e: 
        print(f"Ошибка при получении UUID: {e}") 
        return None         
        

l = hex(int(datetime.datetime.now().timestamp()))
print(l)
print(len(l))
print(get_uuid())
print(len(get_uuid()))
print(hex(int(get_uuid())))

conn = pg.connect(host='10.147.20.167', port=5432, database='lab_1', user='valpc', password='123')
print(conn)

# print(res)
conn.close()


# Данные для хэширования
data = "Пример текста для хэширования"

# Создание объекта sha256
sha256_hash = hashlib.sha256()

# Обновление хэша с помощью данных, преобразованных в байты
sha256_hash.update(data.encode('utf-8'))

# Вычисление хэша и получение его в шестнадцатеричном формате
hashed_data = sha256_hash.hexdigest()

print("SHA-256 хэш:", hashed_data)
print("SHA-256 хэш:", len(hashed_data))



