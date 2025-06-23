# bot/security.py
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from bot.config import config

AUTHORIZED_USERS = set()

class SecurityManager:

    @staticmethod
    def authorize_user(user_id: int):
        AUTHORIZED_USERS.add(user_id)

    @staticmethod
    def is_authorized_user(user_id: int) -> bool:
        return user_id in AUTHORIZED_USERS

    @staticmethod
    def check_pin(pin: str) -> bool:
        return pin == config.PIN_CODE

    @staticmethod
    def encrypt_data(data: str) -> str:
        key = config.AES_KEY.encode()
        salt = b"fixed_salt__"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        token_key = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(token_key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(token: str) -> str:
        key = config.AES_KEY.encode()
        salt = b"fixed_salt__"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000,
        )
        token_key = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(token_key)
        return f.decrypt(token.encode()).decode()