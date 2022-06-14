from re import I, sub
from typing import List
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
    GroupMessageEvent,
    PrivateMessageEvent,
)

from .utils import send_forward_msg
from .config import Config
from .models import Setu, SetuNotFindError
from .withdraw import add_withdraw_job
from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .data_source import SetuLoader

plugin_config = Config.parse_obj(get_driver().config.dict())
SAVE = plugin_config.setu_save
SETU_SIZE = plugin_config.setu_size
MAX = plugin_config.setu_max

if SAVE == "webdav":
    from .save_to_webdav import save_img
elif SAVE == "local":
    from .save_to_local import save_img


plugin_config = Config.parse_obj(get_driver().config.dict())

setu_matcher = on_regex(
    r"^(setu|色图|涩图|来点色色|色色|涩涩|来点色图)\s?([x|✖️|×|X|*]?\d+[张|个|份]?)?\s?(r18)?\s?\s?(tag)?\s?(.*)?",
    flags=I,
    permission=PRIVATE_FRIEND | GROUP,
)


@setu_matcher.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State = State()):
    args = list(state["_matched_groups"])
    num = args[1]
    r18 = args[2]
    tags = args[3]
    key = args[4]

    num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", num)) if num else 1
    if num > MAX:
        num = MAX

    # 如果存在 tag 关键字, 则将 key 视为tag
    if tags:
        tags = key.split()
        key = ""

    # 仅在私聊中开启
    r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await setu_matcher.finish(cd_msg(cd), at_sender=True)

    logger.debug(f"Setu: r18:{r18}, tag:{tags}, key:{key}, num:{num}")
    add_cd(event, num)

    setu_obj = SetuLoader()
    try:
        data = await setu_obj.get_setu(key, tags, r18, num)
    except SetuNotFindError:
        remove_cd(event)
        await setu_matcher.finish(f"没有找到关于 {tags or key} 的色图呢～", at_sender=True)

    failure_msg: int = 0
    msg_list: List[Message] = []

    for setu in data:
        msg = Message(MessageSegment.image(setu.img))  # type: ignore

        if plugin_config.setu_send_info_message:
            msg.append(MessageSegment.text(setu.msg))  # type: ignore

        msg_list.append(msg)  # type: ignore

        if SAVE:
            await save_img(setu)

        # 私聊 或者 群聊中 <= 3 图, 直接发送
    if isinstance(event, PrivateMessageEvent) or len(data) <= 3:
        for msg in msg_list:
            try:
                msg_info = await setu_matcher.send(msg, at_sender=True)
                add_withdraw_job(bot, **msg_info)
                await sleep(2)

            except ActionFailed as e:
                logger.warning(e)
                failure_msg += 1

    # 群聊中 > 3 图, 合并转发
    elif isinstance(event, GroupMessageEvent):

        try:
            await send_forward_msg(bot, event, "好东西", bot.self_id, msg_list)
        except ActionFailed as e:
            logger.warning(e)
            failure_msg = num

    if failure_msg >= num / 2:
        remove_cd(event)

        await setu_matcher.finish(
            message=Message(f"消息被风控，{failure_msg} 个图发不出来了\n"),
            at_sender=True,
        )
