from pydantic import BaseModel, Extra
from typing import Optional


class Config(BaseModel, extra=Extra.ignore):
    superusers: set
    debug: Optional[bool] = False
    setu_cd: int = 60
    setu_save: Optional[str] = None
    setu_path: Optional[str] = None
    setu_proxy: Optional[str] = None
    setu_reverse_proxy: Optional[str] = None
    setu_dav_url: Optional[str] = None
    setu_dav_username: Optional[str] = None
    setu_dav_password: Optional[str] = None
