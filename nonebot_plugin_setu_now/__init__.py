import time
import asyncio
from io import BytesIO
from re import I, sub
from typing import List, Union
from asyncio import create_task
from asyncio.tasks import Task

from PIL import Image, UnidentifiedImageError
from nonebot import get_bot, on_regex, get_driver, on_command
from sqlmodel import select
from nonebot.log import logger
from nonebot.rule import to_me
from nonebot.params import Depends, EventMessage
from nonebot.plugin import require
from nonebot.typing import T_State
from nonebot.matcher import Matcher
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
from sqlmodel.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11.helpers import autorevoke_send

require("nonebot_plugin_datastore")
try:
    from nonebot_plugin_datastore import get_session
except ModuleNotFoundError:
    from ..nonebot_plugin_datastore import get_session

from .utils import SpeedLimiter, send_forward_msg
from .config import MAX, SAVE, EFFECT, WITHDRAW_TIME, Config
from .models import Setu, SetuInfo, MessageInfo, SetuNotFindError
from .database import bind_message_data, auto_upgrade_setuinfo
from .withdraw import add_withdraw_job
from .img_utils import EFFECT_FUNC_LIST, image_segment_convert
from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .perf_timer import PerfTimer
from .data_source import SetuHandler
from .r18_whitelist import get_group_white_list_record

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
async def _(
    bot: Bot,
    event: Union[PrivateMessageEvent, GroupMessageEvent],
    state: T_State,
    db_session: AsyncSession = Depends(get_session),
    white_list_record=Depends(get_group_white_list_record),
):
    # await setu_matcher.finish("服务器维护喵，暂停服务抱歉喵")
    setu_total_timer = PerfTimer("Image request total")
    args = list(state["_matched_groups"])
    num = args[1]
    r18 = args[2]
    tags = args[3]
    key = args[4]

    num = int(sub(r"[张|个|份|x|✖️|×|X|*]", "", num)) if num else 1
    num = min(num, MAX)

    # 如果存在 tag 关键字, 则将 key 视为tag
    if tags:
        tags = list(map(lambda l: l.split("或"), key.split()))
        key = ""

    # 仅在私聊中开启
    # r18 = True if (isinstance(event, PrivateMessageEvent) and r18) else False
    if r18:
        if isinstance(event, PrivateMessageEvent):
            r18 = True
        elif isinstance(event, GroupMessageEvent):
            if white_list_record is None:
                await setu_matcher.finish("不可以涩涩！\n本群未启用R18支持\n请移除R18标签或联系维护组")
            r18 = True

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await setu_matcher.finish(cd_msg(cd))

    logger.debug(f"Setu: r18:{r18}, tag:{tags}, key:{key}, num:{num}")
    add_cd(event, num)

    async def nb_send_handler(setu: Setu) -> None:
        for process_func in EFFECT_FUNC_LIST:
            if r18 and process_func == EFFECT_FUNC_LIST[0]:
                # R18禁止使用默认图像处理方法(do_nothing)
                continue
            logger.debug(f"Using effect {process_func}")
            effert_timer = PerfTimer.start("Effect process")
            try:
                image = process_func(setu.img)  # type: ignore
            except UnidentifiedImageError:
                return
            effert_timer.stop()
            msg = Message(image_segment_convert(image))
            try:
                send_timer = PerfTimer("Image send")
                message_id = 0
                if not WITHDRAW_TIME:
                    # 未设置撤回时间 正常发送
                    message_id: int = (await setu_matcher.send(msg))["message_id"]
                    await auto_upgrade_setuinfo(db_session, setu)
                    await bind_message_data(db_session, message_id, setu.pid)
                    logger.debug(f"Message ID: {message_id}")
                else:
                    logger.debug(f"Using auto revoke API, interval: {WITHDRAW_TIME}")
                    await autorevoke_send(
                        bot=bot, event=event, message=msg, revoke_interval=WITHDRAW_TIME
                    )
                send_timer.stop()

                send_success_state = True
                return
            except ActionFailed:
                if not EFFECT:  # 设置不允许添加特效
                    return
                logger.warning(f"Image send failed, retrying another effect")

    setu_handler = SetuHandler(key, tags, r18, num, nb_send_handler)
    try:
        await setu_handler.process_request()
    except SetuNotFindError:
        remove_cd(event)
        await setu_matcher.finish(f"没有找到关于 {tags or key} 的色图呢～")

    # failure_msg: int = 0
    # msg_list: List[Message] = []
    # forward_send_mode_state = isinstance(event, GroupMessageEvent) or num >= 5
    # """
    # 优先发送原图，当原图发送失败（ActionFailedException）时，尝试逐个更换处理特效发送
    # """
    # for setu in data:

    #     if send_success_state:
    #         continue
    #     failure_msg += 1
    #     logger.warning(f"Image send failed")

    # if failure_msg >= num / 2:
    #     remove_cd(event)

    #     await setu_matcher.finish(
    #         message=Message(f"{failure_msg} 张图片消失了喵"),
    #     )

    # setu_total_timer.stop()
    # if SAVE:
    #     setu_saving_tasks: List[Task] = []
    #     for setu in data:
    #         setu_saving_tasks.append(create_task(save_img(setu)))
    #     await asyncio.gather(*setu_saving_tasks)


setuinfo_matcher = on_command("信息")


@setuinfo_matcher.handle()
async def _(
    event: MessageEvent,
    db_session: AsyncSession = Depends(get_session),
):
    logger.debug("Running setu info handler")
    event_message = event.original_message
    reply_segment = event_message["reply"]
    if reply_segment == []:
        logger.debug("Command invalid: Not specified setu info to get!")
        await setuinfo_matcher.finish("请直接回复需要作品信息的插画")
    reply_segment = reply_segment[0]
    reply_message_id = reply_segment.data["id"]
    logger.debug(f"Get setu info for message id: {reply_message_id}")
    statement = select(MessageInfo).where(MessageInfo.message_id == reply_message_id)
    messageinfo_result: MessageInfo = (await db_session.exec(statement)).first()
    if not messageinfo_result:
        await setuinfo_matcher.finish("未找到该插画相关信息")
    message_pid = messageinfo_result.pid
    statement = select(SetuInfo).where(SetuInfo.pid == message_pid)
    setu_info = (await db_session.exec((statement))).first()
    if not setu_info:
        await setuinfo_matcher.finish("该插画相关信息已被移除")
    info_message = MessageSegment.text(f"标题：{setu_info.title}\n")
    info_message += MessageSegment.text(f"画师：{setu_info.author}\n")
    info_message += MessageSegment.text(f"PID：{setu_info.pid}")
    await setu_matcher.finish(MessageSegment.reply(reply_message_id) + info_message)
