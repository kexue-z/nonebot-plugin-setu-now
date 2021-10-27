import random
from re import I

import nonebot
from nonebot import on_command, on_regex
from nonebot.adapters.cqhttp import (
    Bot,
    Event,
    Message,
    PrivateMessageEvent,
)
from nonebot.adapters.cqhttp.permission import GROUP, PRIVATE_FRIEND
from nonebot.log import logger
from nonebot.typing import T_State
from .get_Data import get_setu
from .setu_Message import *
from .json_Manager import *


setu = on_regex(
    r"^(setu|色图|涩图|来点色色|色色)\s?(r18)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)
withdraw = on_command("撤回")
cdTime = (
    nonebot.get_driver().config.setu_cd if nonebot.get_driver().config.setu_cd else 60
)



@setu.handle()
async def _(bot: Bot, event: Event, state: T_State):
    global mid
    args = list(state["_matched_groups"])
    r18 = args[1]
    key = args[2]
    qid = event.get_user_id()
    mid = event.message_id
    data = readJson()
    try:
        cd = event.time - data[qid][0]
    except:
        cd = cdTime + 1

    r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False

    logger.info(f"key={key},r18={r18}")

    if cd > cdTime or event.get_user_id() in nonebot.get_driver().config.superusers:
        writeJson(qid, event.time, mid, data)
        pic = await get_setu(key, r18)
        if pic[2]:
            try:
                await setu.send(message=Message(pic[0]))
                await setu.send(
                    message=f"{random.choice(setu_SendMessage)}\n" + Message(pic[1]),
                    at_sender=True,
                )
            except Exception as e:
                logger.warning(e)
                removeJson(qid)
                await setu.finish(
                    message=Message(f"消息被风控，图发不出来\n{pic[1]}\n这是链接\n{pic[3]}"),
                    at_sender=True,
                )

        else:
            removeJson(qid)
            await setu.finish(pic[0] + pic[1])

    else:
        await setu.send(
            f"{random.choice(setu_SendCD)} 你的CD还有{cdTime - cd}秒", at_sender=True
        )
