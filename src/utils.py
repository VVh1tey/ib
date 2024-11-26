import re

def validate_login(login):
    return bool(re.fullmatch(r'\d{4}', login))

def validate_password(password):
    return len(password) == 10 and bool(re.search(r'[a-zA-Z]', password)) and bool(re.search(r'\d', password))