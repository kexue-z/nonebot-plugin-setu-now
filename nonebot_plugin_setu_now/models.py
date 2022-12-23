from typing import Dict, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Column, SQLModel


class SetuData(BaseModel):
    title: str
    urls: Dict[str, str]
    author: str
    tags: List[str]
    pid: int
    p: int
    r18: bool


class SetuApiData(BaseModel):
    error: Optional[str]
    data: List[SetuData]


class Setu:
    def __init__(self, data: SetuData):
        self.title: str = data.title
        self.urls: Dict[str, str] = data.urls
        self.author: str = data.author
        self.tags: List[str] = data.tags
        self.pid: int = data.pid
        self.p: int = data.p
        self.r18: bool = data.r18
        self.img: Optional[bytes] = None
        self.msg: Optional[str] = None


class SetuMessage(BaseModel):
    send: List[str]
    cd: List[str]


class SetuNotFindError(Exception):
    pass


class SetuInfo(SQLModel, table=True):
    __tablename__: str = "setu_data"
    message_id: int = Field(default=0, primary_key=True, unique=True)
    author: str = Field(default="Unknown")
    title: str = Field(default="Unknown")
    pid: int = Field(default=0, unique=True)


class GroupWhiteListRecord(SQLModel, table=True):
    __tablename__: str = "white_list"
    group_id: int = Field(default=None, primary_key=True, unique=True)
    operator_user_id: int = Field(default=None)
