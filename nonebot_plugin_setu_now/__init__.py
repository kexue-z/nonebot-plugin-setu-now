from re import I
from typing import Optional
from asyncio import sleep

from nonebot import on_regex, get_driver
from nonebot.log import logger
from nonebot.params import State
from nonebot.typing import T_State
from nonebot.exception import ActionFailed
from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)

from .config import Config
from .models import Setu, SetuNotFindError
from .withdraw import add_withdraw_job
from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .data_source import SetuLoader

plugin_config = Config.parse_obj(get_driver().config.dict())
SAVE = plugin_config.setu_save
SETU_SIZE = plugin_config.setu_size

if SAVE == "webdav":
    from .save_to_webdav import save_img
elif SAVE == "local":
    from .save_to_local import save_img


plugin_config = Config.parse_obj(get_driver().config.dict())

setu_matcher = on_regex(
    r"^(setu|色图|涩图|来点色色|色色|涩涩)\s?(r18)?\s?(tag)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)


@setu_matcher.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    args = list(state["_matched_groups"])
    r18 = args[1]
    tags = args[2]
    key = args[3]
    num = 1

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await setu_matcher.finish(cd_msg(cd), at_sender=True)

    r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False

    logger.debug(f"Setu: r18:{r18}, tag:{tags}, key:{key}, num:{num}")
    add_cd(event)

    setu_obj = SetuLoader()
    try:
        data = await setu_obj.get_setu(key, tags, r18, num)
    except SetuNotFindError:
        remove_cd(event)
        await setu_matcher.finish(f"没有找到关于 {tags or key} 的色图呢～", at_sender=True)
    # failure = 0
    failure_setu: list[Setu] = []

    for setu in data:
        try:
            msg = Message(MessageSegment.image(setu.img))  # type: ignore

            if plugin_config.setu_send_info_message:
                msg.append(MessageSegment.text(setu.msg))  # type: ignore

            msg_info = await setu_matcher.send(msg, at_sender=True)

            add_withdraw_job(bot, **msg_info)

            await sleep(2)

        except ActionFailed as e:
            logger.warning(e)
            failure_setu.append(setu)

        if SAVE:
            await save_img(setu)

    if len(failure_setu) >= num / 2:
        remove_cd(event)
        msg = ""
        for setu in failure_setu:
            msg += setu.urls[SETU_SIZE] + "\n"

        await setu_matcher.finish(
            message=Message("消息被风控，图发不出来\n这是链接\n" + msg),
            at_sender=True,
        )
