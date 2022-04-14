from pydantic import BaseModel
from typing import Optional, List


class SetuData(BaseModel):
    title: str
    urls: dict[str, str]
    author: str
    tags: list[str]
    pid: int
    p: int
    r18: bool


class SetuApiData(BaseModel):
    error: Optional[str]
    data: List[SetuData]


class Setu:
    def __init__(self, data: List[SetuData]):
        self.data: List[SetuData] = data
        self.img: Optional[List[bytes]] = []
        self.msg: Optional[List[str]] = []


class SetuMessage(BaseModel):
    send: list[str]
    cd: list[str]
