from dataclasses import dataclass


@dataclass
class DBCredits:
    uri: str = ""
    user: str = ""
    password: str = ""
