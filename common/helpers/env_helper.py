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
BASE_URL_LIS: str = (lambda split_url: f"{split_url[0]}:{split_url[1]}:47205")(BASE_URL.split(":"))


@dataclass()
class UserData:
    login: str = get_var_from_env("USER_LOGIN")
    password: str = get_var_from_env("USER_PASS")
