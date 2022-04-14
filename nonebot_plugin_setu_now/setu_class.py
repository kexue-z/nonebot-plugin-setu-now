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
    img: Optional[bytes]


class SetuApiData(BaseModel):
    error: Optional[str]
    data: List[SetuData]
