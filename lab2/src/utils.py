import bcrypt
import random
import string
from PIL import Image, ImageDraw, ImageFont

# Работа с паролями
def generate_salt():
    return bcrypt.gensalt()

def hash_password(password, salt):
    if not bcrypt.checkpw(b"", salt):  # Проверяем, что соль валидна
        raise ValueError("Invalid salt provided for bcrypt.")
    return bcrypt.hashpw(password.encode(), salt)

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

# Генерация капчи
def generate_captcha():
    captcha_text = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    image = Image.new('RGB', (200, 80), color=(255, 255, 255))
    font = ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    draw.text((50, 20), captcha_text, fill=(0, 0, 0), font=font)
    image.save("captcha.png")
    return captcha_text
