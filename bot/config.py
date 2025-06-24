# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID"))
    PIN_CODE = os.getenv("PIN_CODE")
    MAX_PIN_ATTEMPTS = int(os.getenv("MAX_PIN_ATTEMPTS"))
    AES_KEY = os.getenv("AES_KEY")
    DATA_FILE = os.getenv("DATA_FILE")
    TRON_NETWORK = os.getenv("TRON_NETWORK", "nile")
    USDT_CONTRACT_ADDRESS = os.getenv("USDT_CONTRACT_ADDRESS")

config = Config()