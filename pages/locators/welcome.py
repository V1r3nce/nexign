from dataclasses import dataclass


@dataclass
class WelcomePage:
    input_login: str = 'login'
    input_password: str = 'password'
    login_submit: str = 'enterBtn'
    menu: str = '.collect-candy-button'
    logout: str = 'sc-gLLuof Oqokr'
