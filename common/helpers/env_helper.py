import os
import re
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_var_from_env(var_name: str, default_value: str | None = None) -> str:
    var = os.getenv(var_name, default_value)
    if var is None:
        raise ValueError(f"Не найдена переменная окружения {var_name}.\n Проверьте наличие переменной в .env файле.")
    return var


BASE_URL_API: str = get_var_from_env("BASE_URL")
BASE_URL: str = get_var_from_env("BASE_URL") + "/nbss/"
BASE_URL_RFD: str = (lambda split_url: f"{split_url[0]}:{split_url[1]}:47222")(BASE_URL.split(":"))
BASE_URL_LIS: str = (lambda split_url: f"{split_url[0]}:{split_url[1]}:47205")(BASE_URL.split(":"))
BASE_URL_PSC: str = (lambda split_url: f"{split_url[0]}:{split_url[1]}:10099")(BASE_URL.split(":"))
BASE_URL_CRAB: str = (lambda split_url: f"{split_url[0]}:{split_url[1].replace('sso', 'crab-ui')}:18240")(
    BASE_URL.split(":")
)
BASE_URL_UDB = (lambda split_url: f"{split_url[0]}:{split_url[1]}:47224")(BASE_URL.split(":"))
BASE_URL_STANDHELPER = re.sub(
    r"//srv-app\d\d|//np|//sso",
    "//standhelper.k8s",
    ((lambda split_url: f"{split_url[0]}:{split_url[1]}")(BASE_URL.split(":"))),
)
PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent.parent
TEMP_DIR: Path = PROJECT_ROOT_PATH / "tmp"
HAR_DIR: Path = TEMP_DIR / "har"
DOWNLOAD_DIR: Path = TEMP_DIR / "download"
LOGS_FOLDER: Path = TEMP_DIR / "logs"


@dataclass()
class UserData:
    login: str = get_var_from_env("USER_LOGIN")
    password: str = get_var_from_env("USER_PASS")


@dataclass()
class UniblpUserData:
    login: str = get_var_from_env("UNIBLP_USER_LOGIN")
    password: str = get_var_from_env("UNIBLP_USER_PASS")


def get_user_by_role(role_name: str) -> tuple[str, str]:
    if role_name == "Admin":
        return get_var_from_env("USER_LOGIN"), get_var_from_env("USER_PASS")

    role_prefix = role_name.replace("_TEST", "")
    login = get_var_from_env(f"{role_prefix}_LOGIN", role_name)
    password = get_var_from_env(f"{role_prefix}_PASS")
    return login, password
