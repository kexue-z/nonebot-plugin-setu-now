import time
import base64
import asyncio
from io import BytesIO
from re import I, sub
from typing import List, Union
from asyncio import sleep, create_task
from asyncio.tasks import Task

from PIL import Image
from nonebot import on_regex, get_driver
from nonebot.log import logger
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

from .utils import send_forward_msg
from .config import Config
from .models import Setu, SetuNotFindError
from .withdraw import add_withdraw_job
from .img_utils import EFFECT_FUNC_LIST
from .cd_manager import add_cd, cd_msg, check_cd, remove_cd
from .data_source import SetuLoader
from .r18_whitelist import group_r18_whitelist_checker

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
async def _(
    bot: Bot, event: Union[PrivateMessageEvent, GroupMessageEvent], state: T_State
):
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
    """
    优先发送原图，当原图发送失败（ActionFailedException）时，尝试逐个更换处理特效发送
    """
    for setu in data:
        send_success_state = False
        if SAVE:
            setu_saving_tasks.append(create_task(save_img(setu)))
        for process_func in EFFECT_FUNC_LIST:
            logger.debug(f"Using effect {process_func}")
            start_time = time.time()
            image = process_func(Image.open(BytesIO(setu.img)))  # type: ignore
            logger.debug(
                f"Effect filter use {round(time.time() - start_time,2)}s to process image"
            )
            image_bytesio = BytesIO()
            logger.debug(f"Saving image: {image.width} x {image.height}")
            start_time = time.time()
            if image.mode != "RGB":
                image = image.convert("RGB")
            if image.format in ("JPEG", "JPG"):
                image.save(image_bytesio, format="JPEG", quality="keep")
            else:
                image.save(image_bytesio, format="JPEG", quality=95)
            logger.debug(f"Image use {round(time.time() - start_time,2)}s to save")
            msg = Message(MessageSegment.image(image_bytesio))  # type: ignore
            if plugin_config.setu_send_info_message:
                msg.append(MessageSegment.text(setu.msg))  # type: ignore
            try:
                logger.warning(f"Trying sending image using effect {process_func}")
                await setu_matcher.send(msg)
                send_success_state = True
                break
            except ActionFailed:
                logger.warning(f"Image send failed, retrying another effect")
        if send_success_state:
            msg_list.append(msg)  # type: ignore
            continue
        failure_msg += 1
        logger.warning(f"Image send failed after retrying all effect")

    if failure_msg >= num / 2:
        remove_cd(event)

        await setu_matcher.finish(
            message=Message(f"共 {failure_msg} 张图片发送失败"),
        )

    await asyncio.gather(*setu_saving_tasks)
