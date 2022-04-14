from random import choice
from asyncio import sleep
from re import I

from nonebot import get_driver, on_regex
from nonebot.adapters.onebot.v11 import (
    GROUP,
    PRIVATE_FRIEND,
    Bot,
    Message,
    MessageEvent,
    MessageSegment,
    PrivateMessageEvent,
)
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import State
from nonebot.typing import T_State

from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .config import Config
from .data_source import SetuLoader
from .withdraw import add_withdraw_job
from .setu_message import SetuMessage

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

    if cd := check_cd(event):
        # 如果不满足CD 则直接结束
        await setu_matcher.finish(cd_msg(cd), at_sender=True)

    r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False

    add_cd(event)

    setu = SetuLoader()
    data = await setu.get_setu(key, tags, r18)
    try:
        for i in data.data:

            msg_info = await setu.send(message=MessageSegment.image(i.img))  # type: ignore
            add_withdraw_job(bot, **msg_info)

            # 是否需要发送图片消息
            if plugin_config.setu_send_info_message:
                await sleep(2)
                msg_info = await setu.send(
                    message=f"{choice(SetuMessage.send)}"  # 发送一些消息
                    + Message(setu.setu_info_msg()),
                    at_sender=True,
                )
                add_withdraw_job(bot, **msg_info)

    except ActionFailed as e:
        logger.warning(e)
        remove_cd(event)
        await setu.finish(
            message=Message(f"消息被风控，图发不出来\n{pic[1]}\n这是链接\n{pic[3]}"),
            at_sender=True,
        )
