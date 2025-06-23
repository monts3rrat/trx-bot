# bot\security.py

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from bot.config import config
from aiogram.fsm.context import FSMContext

class SecurityManager:
    @staticmethod
    def is_authorized_user(user_id: int) -> bool:
        return user_id == config.ADMIN_TELEGRAM_ID
    
    @staticmethod
    def check_pin(pin: str) -> bool:
        return pin == config.PIN_CODE
    
    @staticmethod
    def encrypt_data(data: str) -> str:
        key = config.AES_KEY.encode()
        salt = b'salt_'  # Используем фиксированную соль для упрощения
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_derived = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(key_derived)
        encrypted_data = f.encrypt(data.encode())
        return encrypted_data.decode()
    
    @staticmethod
    def decrypt_data(encrypted_data: str) -> str:
        key = config.AES_KEY.encode()
        salt = b'salt_'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key_derived = base64.urlsafe_b64encode(kdf.derive(key))
        f = Fernet(key_derived)
        decrypted_data = f.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    
    @staticmethod
    async def check_auth(message, state: FSMContext) -> bool:
        data = await state.get_data()
        return data.get("authenticated", False)