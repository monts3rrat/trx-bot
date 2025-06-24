# bot\config.py

import os
from dotenv import load_dotenv

# загружаем .env
load_dotenv()

class Config:
    BOT_TOKEN               = os.getenv("BOT_TOKEN")
    ADMIN_TELEGRAM_ID       = int(os.getenv("ADMIN_TELEGRAM_ID", 0))
    PIN_CODE                = os.getenv("PIN_CODE")
    MAX_PIN_ATTEMPTS        = int(os.getenv("MAX_PIN_ATTEMPTS", 3))
    AES_KEY                 = os.getenv("AES_KEY")
    DATA_FILE               = os.getenv("DATA_FILE", "data/dummy_data.json")
    TRON_NETWORK            = os.getenv("TRON_NETWORK", "mainnet")
    USDT_CONTRACT_ADDRESS   = os.getenv(
        "USDT_CONTRACT_ADDRESS",
        "TXYZopYRdj2D9XRtbG411XZZ3kM5VkAeBf"
    )
    TRONGRID_API_KEY        = os.getenv("TRONGRID_API_KEY")

config = Config()