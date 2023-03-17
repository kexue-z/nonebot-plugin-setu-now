from typing import Dict, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class SetuData(BaseModel):
    pid: int
    p: int
    uid: int
    title: str
    author: str
    r18: bool
    width: int
    height: int
    tags: List[str]
    ext: str
    aiType: int
    uploadDate: int
    urls: Dict[str, str]


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
        self.ext: str = data.ext
        self.img: Optional[str] = None
        self.msg: Optional[str] = None


class SetuMessage(BaseModel):
    send: List[str]
    cd: List[str]


class SetuNotFindError(Exception):
    pass


class SetuInfo(SQLModel, table=True):
    __tablename__: str = "setu_info"
    pid: int = Field(default=None, primary_key=True, unique=True)
    author: str = Field(default=None)
    title: str = Field(default=None)
    url: str = Field(default=None)


class MessageInfo(SQLModel, table=True):
    __tablename__: str = "message_data"
    message_id: int = Field(default=None, primary_key=True, unique=True)
    pid: int = Field(default=None)


class GroupWhiteListRecord(SQLModel, table=True):
    __tablename__: str = "white_list"
    group_id: int = Field(default=None, primary_key=True, unique=True)
    operator_user_id: int = Field(default=None)
