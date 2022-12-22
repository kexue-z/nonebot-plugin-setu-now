import time
import asyncio
from io import BytesIO
from re import I, sub
from typing import List, Union
from asyncio import create_task
from asyncio.tasks import Task

from PIL import Image
from nonebot import on_regex, get_driver, on_command
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

from .utils import send_forward_msg
from .config import Config
from .models import Setu, SetuInfo, SetuNotFindError
from .withdraw import add_withdraw_job
from .img_utils import EFFECT_FUNC_LIST
from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .perf_timer import PerfTimer
from .data_source import SetuLoader
from .r18_whitelist import group_r18_whitelist_checker

require("nonebot_plugin_datastore")
from ..nonebot_plugin_datastore import get_session

plugin_config = Config.parse_obj(get_driver().config.dict())
SAVE = plugin_config.setu_save
SETU_SIZE = plugin_config.setu_size
MAX = plugin_config.setu_max
EFFECT = plugin_config.setu_add_random_effect
SEND_INTERVAL = plugin_config.setu_minimum_send_interval

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
):
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
            if not group_r18_whitelist_checker.check_is_group_in_whitelist(
                event.group_id
            ):
                await setu_matcher.finish("不可以涩涩！\n本群未启用R18支持，请移除R18标签或联系维护组")
            r18 = True

    if cd := check_cd(event):
        # 如果 CD 还没到 则直接结束
        await setu_matcher.finish(cd_msg(cd))

    logger.debug(f"Setu: r18:{r18}, tag:{tags}, key:{key}, num:{num}")
    add_cd(event, num)

    setu_obj = SetuLoader()
    try:
        data = await setu_obj.get_setu(key, tags, r18, num)
    except SetuNotFindError:
        remove_cd(event)
        await setu_matcher.finish(f"没有找到关于 {tags or key} 的色图呢～")

    failure_msg: int = 0
    msg_list: List[Message] = []
    setu_saving_tasks: List[Task] = []
    forward_send_mode_state = isinstance(event, GroupMessageEvent) or num >= 5
    """
    优先发送原图，当原图发送失败（ActionFailedException）时，尝试逐个更换处理特效发送
    """
    last_send_time = 0
    for setu in data:
        send_success_state = False
        if SAVE:
            setu_saving_tasks.append(create_task(save_img(setu)))
        for process_func in EFFECT_FUNC_LIST:
            logger.debug(f"Using effect {process_func}")
            effert_timer = PerfTimer.start("Effect process")
            image = process_func(Image.open(BytesIO(setu.img)))  # type: ignore
            effert_timer.stop()
            image_bytesio = BytesIO()
            save_timer = PerfTimer.start(f"Save bytes {image.width} x {image.height}")
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(
                image_bytesio,
                format="JPEG",
                quality="keep" if image.format in ("JPEG", "JPG") else 95,
            )
            save_timer.stop()
            msg = Message(MessageSegment.image(image_bytesio))  # type: ignore
            if plugin_config.setu_send_info_message:
                msg.append(MessageSegment.text(setu.msg))  # type: ignore
            try:
                send_timer = PerfTimer("Image send")
                if (delay_time := time.time() - last_send_time) < SEND_INTERVAL:
                    delay_time = round(delay_time, 2)
                    logger.debug(f"Speed limit: Asyncio sleep {delay_time}s")
                    await asyncio.sleep(delay_time)
                message_id: int = (await setu_matcher.send(msg))["message_id"]
                logger.debug(f"Message ID: {message_id}")
                last_send_time = time.time()
                send_timer.stop()
                db_session.add(
                    SetuInfo(
                        message_id=int(message_id),
                        author=setu.author,
                        title=setu.title,
                        pid=int(setu.pid),
                    )
                )
                await db_session.commit()
                send_success_state = True
                break
            except ActionFailed:
                if not EFFECT:  # 设置不允许添加特效
                    break
                logger.warning(f"Image send failed, retrying another effect")
        if send_success_state:
            continue
        failure_msg += 1
        logger.warning(f"Image send failed")

    if failure_msg >= num / 2:
        remove_cd(event)

        await setu_matcher.finish(
            message=Message(f"共 {failure_msg} 张图片发送失败"),
        )

    setu_total_timer.stop()

    await asyncio.gather(*setu_saving_tasks)


setuinfo_matcher = on_command("信息")


@setuinfo_matcher.handle()
async def _(
    event: MessageEvent,
    db_session: AsyncSession = Depends(get_session),
):
    logger.debug("Running setu info handler")
    event_message = event.original_message
    reply_segment = event_message["reply"]
    for i in event_message:
        logger.debug(i.type)
    if reply_segment == []:
        logger.debug("Command invalid: Not specified setu info to get!")
        await setuinfo_matcher.finish("请直接回复需要作品信息的插画")
    reply_segment = reply_segment[0]
    reply_message_id = reply_segment.data["id"]
    logger.debug(f"Get setu info for message id: {reply_message_id}")
    statement = select(SetuInfo).where(SetuInfo.message_id == reply_message_id)
    setu_info = (await db_session.exec(statement)).first()
    if not setu_info:
        await setuinfo_matcher.finish("未找到该插画相关信息")
    info_message = MessageSegment.text("插画信息：\n")
    info_message += MessageSegment.text(f"标题：{setu_info.title}\n")
    info_message += MessageSegment.text(f"画师：{setu_info.author}\n")
    info_message += MessageSegment.text(f"PID：{setu_info.pid}")
    await setu_matcher.finish(MessageSegment.reply(reply_message_id) + info_message)
