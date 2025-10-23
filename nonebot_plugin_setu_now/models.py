from pathlib import Path

from pydantic import BaseModel


class SetuData(BaseModel):
    pid: int
    p: int
    uid: int
    title: str
    author: str
    r18: bool
    width: int
    height: int
    tags: list[str]
    ext: str
    aiType: int
    uploadDate: int
    urls: dict[str, str]


class SetuApiData(BaseModel):
    error: str | None
    data: list[SetuData]


class Setu:
    def __init__(self, data: SetuData):
        self.title: str = data.title
        self.urls: dict[str, str] = data.urls
        self.author: str = data.author
        self.tags: list[str] = data.tags
        self.pid: int = data.pid
        self.p: int = data.p
        self.r18: bool = data.r18
        self.ext: str = data.ext
        self.img: Path | None = None
        self.msg: str | None = None


class SetuMessage(BaseModel):
    send: list[str]
    cd: list[str]


class SetuNotFindError(Exception):
    pass
