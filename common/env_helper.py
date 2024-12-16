from dataclasses import dataclass
from pathlib import Path
import os
from dotenv import load_dotenv


ENV_FILE = '.env'
APP_DIR = Path(__file__).parent.parent
ENV_FILE_PATH: Path = APP_DIR / ENV_FILE

if ENV_FILE_PATH.exists():
    load_dotenv(ENV_FILE_PATH)
else:
    print("Not")

BASE_URL_API: str = os.environ["BASE_URL_API"]


@dataclass()
class UserData:
    login: str = os.environ["USER_LOGIN"]
    password: str = os.environ["USER_PASS"]
