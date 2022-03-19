import random
from re import I

from nonebot import get_driver, on_regex
from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import State
from nonebot.typing import T_State

from .config import Config
from .get_data import get_setu
from .json_manager import read_json, remove_json, write_json
from .setu_message import load_setu_message

driver = get_driver()
plugin_config = Config.parse_obj(get_driver().config.dict())
CDTIME = plugin_config.setu_cd


@driver.on_startup
async def init():
    """启动时加载setumsg"""
    global SETU_MSG
    SETU_MSG = await load_setu_message()
    return SETU_MSG


setu = on_regex(
    r"^(setu|色图|涩图|来点色色|色色|涩涩)\s?(r18)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)


@setu.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    global mid
    args = list(state["_matched_groups"])
    r18 = args[1]
    key = args[2]
    qid = event.get_user_id()
    mid = event.message_id
    data = read_json()
    try:
        cd = event.time - data[qid][0]
    except Exception:
        cd = CDTIME + 1

    r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False

    logger.debug(f"key={key},r18={r18}")

    if (
        cd > CDTIME
        or event.get_user_id() in plugin_config.superusers
        or isinstance(event, PrivateMessageEvent)
    ):
        write_json(qid, event.time, mid, data)
        pic = await get_setu(key, r18)
        if pic[2]:
            try:

                await setu.send(message=Message(pic[0]))
                # 是非需要发送图片消息
                if plugin_config.setu_send_info_message:
                    await setu.send(
                        message=f"{random.choice(SETU_MSG['setu_message_send'])}\n"  # 发送一些消息
                        + Message(pic[1]),
                        at_sender=True,
                    )
            except ActionFailed as e:
                logger.warning(e)
                remove_json(qid)
                await setu.finish(
                    message=Message(f"消息被风控，图发不出来\n{pic[1]}\n这是链接\n{pic[3]}"),
                    at_sender=True,
                )

        else:
            remove_json(qid)
            await setu.finish(pic[0] + pic[1])

    else:
        time_last = CDTIME - cd
        hours, minutes, seconds = 0, 0, 0
        if time_last >= 60:
            minutes, seconds = divmod(time_last, 60)
            hours, minutes = divmod(minutes, 60)
        else:
            seconds = time_last
        cd_msg = f"{str(hours) + '小时' if hours else ''}{str(minutes) + '分钟' if minutes else ''}{str(seconds) + '秒' if seconds else ''}"

        await setu.send(
            random.choice(SETU_MSG["setu_message_cd"]).format(cd_msg),
            at_sender=True,
        )
