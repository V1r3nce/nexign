from dataclasses import dataclass
import os
from dotenv import load_dotenv


load_dotenv()


def get_var_from_env(var_name):
    var = os.getenv(var_name)
    if var is None:
        raise ValueError(f'Не найдена переменная окружения {var_name}.\n Проверьте наличие переменной в .env файле.')
    return var


BASE_URL_API: str = get_var_from_env("BASE_URL")
BASE_URL: str = get_var_from_env("BASE_URL") + "/rm-ui/all/"


@dataclass()
class UserData:
    login: str = os.environ["USER_LOGIN"]
    password: str = os.environ["USER_PASS"]
