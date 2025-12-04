from dataclasses import dataclass
from random import choice
from typing import List


@dataclass
class IPInfo:
    address: str
    id: int


@dataclass
class APNInfo:
    name: str
    id: int
    hlr_id: int
    free_ip_list: List[IPInfo]

    def __init__(self, name: str, id: int, hlr_id: int):
        self.name = name
        self.id = id
        self.hlr_id = hlr_id
        self.free_ip_list = []

    def pop_random(self) -> IPInfo:
        index = choice(range(len(self.free_ip_list)))
        return self.free_ip_list.pop(index)
