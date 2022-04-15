from typing import List, Optional

from pydantic import BaseModel


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
    def __init__(self, data: SetuData):
        self.title: str = data.title
        self.urls: dict[str, str] = data.urls
        self.author: str = data.author
        self.tags: list[str] = data.tags
        self.pid: int = data.pid
        self.p: int = data.p
        self.r18: bool = data.r18
        self.img: Optional[bytes] = None
        self.msg: Optional[str] = None


class SetuMessage(BaseModel):
    send: list[str]
    cd: list[str]


class SetuNotFindError(Exception):
    pass
