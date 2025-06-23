import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def encrypt_data(data: str, password: str, salt: bytes) -> str:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key_derived = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    f = Fernet(key_derived)
    encrypted_data = f.encrypt(data.encode())
    return encrypted_data.decode()

password = "/42bDv9WXKVM54ajqZOT3g=="
salt = os.urandom(16)  # Generate a random salt
private_key = "410140de561171bc76c716365ec73d0bac00ab3e348371a9a1fb7ff5fc090645"
encrypted = encrypt_data(private_key, password, salt)
print(f"Salt (base64): {base64.urlsafe_b64encode(salt).decode()}")
print(f"Encrypted: {encrypted}")
