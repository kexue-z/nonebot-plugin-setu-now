from typing import Optional

from nonebot import get_driver
from pydantic import Extra, BaseModel


class Config(BaseModel, extra=Extra.ignore):
    superusers: set
    debug: Optional[bool] = False
    setu_cd: int = 60
    setu_send_info_message: Optional[bool] = True
    setu_send_custom_message_path: Optional[str] = None
    setu_path: Optional[str] = None
    setu_proxy: Optional[str] = None
    setu_withdraw: Optional[int] = None
    setu_reverse_proxy: str = "i.pixiv.re"
    setu_size: str = "regular"
    setu_api_url: str = "https://api.lolicon.app/setu/v2"
    setu_max: int = 30
    setu_add_random_effect: bool = True
    setu_minimum_send_interval: int = 3


plugin_config = Config.parse_obj(get_driver().config.dict())
SETU_PATH = plugin_config.setu_path
SETU_SIZE = plugin_config.setu_size
MAX = plugin_config.setu_max
EFFECT = plugin_config.setu_add_random_effect
SEND_INTERVAL = plugin_config.setu_minimum_send_interval
WITHDRAW_TIME = plugin_config.setu_withdraw
CDTIME = plugin_config.setu_cd
API_URL = plugin_config.setu_api_url
REVERSE_PROXY = plugin_config.setu_reverse_proxy
PROXY = plugin_config.setu_proxy
