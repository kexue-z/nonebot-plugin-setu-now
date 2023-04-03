from typing import Dict, List, Optional
from pathlib import Path

from pydantic import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from nonebot_plugin_datastore import get_plugin_data

Base = get_plugin_data().Model


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
        self.img: Optional[Path] = None
        self.msg: Optional[str] = None


class SetuMessage(BaseModel):
    send: List[str]
    cd: List[str]


class SetuNotFindError(Exception):
    pass


class SetuInfo(Base):
    __tablename__: str = "setu_info"
    pid: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str]
    title: Mapped[str]
    url: Mapped[str]


class MessageInfo(Base):
    __tablename__: str = "message_data"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    pid: Mapped[int]


class GroupWhiteListRecord(Base):
    __tablename__: str = "white_list"
    group_id: Mapped[int] = mapped_column(primary_key=True)
    operator_user_id: Mapped[int]
