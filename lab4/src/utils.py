import bcrypt
import random
import string
from PIL import Image, ImageDraw, ImageFont
import re

# Работа с паролями
def generate_salt():
    return bcrypt.gensalt()

def hash_password(password, salt):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password, hashed_password):
    if isinstance(hashed_password, str):
        hashed_password_bytes = hashed_password.encode('utf-8')
    else:
        hashed_password_bytes = hashed_password

    if bcrypt.checkpw(password.encode('utf-8'), hashed_password_bytes):
        return True
    else:
        return False

def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    image = Image.new('RGB', (200, 80), color=(255, 255, 255))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    draw.text((50, 20), captcha_text, fill=(0, 0, 0), font=font)
    image.save("lab2/tmp/captcha.png")
    return captcha_text

def validate_login(login):
    return bool(re.fullmatch(r'\d{4}', login))

def validate_password(password):
    return len(password) >= 6 and bool(re.search(r'[a-zA-Z]', password)) and bool(re.search(r'\d', password))