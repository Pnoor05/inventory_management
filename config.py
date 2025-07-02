import os
import re
from dotenv import load_dotenv
from pathlib import Path

def clean_env_value(value):
    """Remove comments and whitespace from env values"""
    if value:
        # Remove everything after # and strip whitespace
        return re.sub(r'#.*$', '', value).strip()
    return value

# Load .env from absolute path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    # Database configuration with strict cleaning
    DB_HOST = clean_env_value(os.getenv('DB_HOST', 'localhost'))
    DB_USER = clean_env_value(os.getenv('DB_USER', 'root'))
    DB_PASSWORD = clean_env_value(os.getenv('DB_PASSWORD', ''))
    DB_NAME = clean_env_value(os.getenv('DB_NAME', 'inventory_db'))

    # Define SECRET_KEY directly using os.getenv
    SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())
    
    @classmethod
    def validate(cls):
        print("\n=== Validated Configuration ===")
        print(f"DB_USER: '{cls.DB_USER}' (length: {len(cls.DB_USER)})")
        print(f"DB_PASSWORD: {'*' * len(cls.DB_PASSWORD) if cls.DB_PASSWORD else '<empty>'}")
        print("==============================")
        # Add validation for SECRET_KEY
        print(f"SECRET_KEY: {'*' * len(cls.SECRET_KEY) if cls.SECRET_KEY else '<empty>'}\n")
        print("===============================")

# Conditional validation call
if __name__ == "__main__":
    Config.validate()