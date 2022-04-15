from random import choice

from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import MessageEvent, PrivateMessageEvent

from .config import Config
from .setu_message import SETU_MSG

driver = get_driver()
plugin_config = Config.parse_obj(get_driver().config.dict())
SUPERUSERS = plugin_config.superusers
CDTIME = plugin_config.setu_cd

cd_data: dict[str, int] = {}


def check_cd(event: MessageEvent) -> int:
    """
    :说明: `check_cd`
        * 检查是否达到CD时间\n
        * 如果达到则返回 `0`\n
        * 如果未达到则返回 `剩余CD时间`


    :参数:
      * `event: MessageEvent`: 事件对象

    :返回:
      - `int`: 时间差
    """
    # cd =  当前时间 - 上一次记录的时间
    try:
        cd: int = event.time - cd_data[event.get_user_id()]
        logger.debug(f"{event.get_user_id()} cd: {cd} 还剩: {CDTIME - cd}")
    except KeyError:
        cd = CDTIME + 1
    if (
        cd > CDTIME
        or event.get_user_id() in SUPERUSERS
        or isinstance(event, PrivateMessageEvent)
    ):
        return 0
    else:
        return cd


def add_cd(event: MessageEvent):
    """添加CD"""
    cd_data[event.get_user_id()] = event.time
    logger.debug("色图CD: {}".format(cd_data))


def remove_cd(event: MessageEvent):
    """移除CD"""
    cd_data.pop(event.get_user_id())
    logger.debug("色图CD: {}".format(cd_data))


def cd_msg(cd) -> str:
    """获取CD提示信息"""
    time_last = CDTIME - cd
    hours, minutes, seconds = 0, 0, 0
    if time_last >= 60:
        minutes, seconds = divmod(time_last, 60)
        hours, minutes = divmod(minutes, 60)
    else:
        seconds = time_last
    cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

    return choice(SETU_MSG.cd).format(cd_msg=cd_msg)
