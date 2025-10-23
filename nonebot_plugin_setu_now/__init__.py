from nonebot import require

require("nonebot_plugin_localstore")
require("nonebot_plugin_orm")

import asyncio
from pathlib import Path

from arclet.alconna import Alconna, Args, Option, action
from nonebot import Bot
from nonebot.exception import ActionFailed
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.plugin import PluginMetadata
from nonebot_plugin_alconna import Arparma, CommandMeta, UniMessage, on_alconna
from nonebot_plugin_uninfo import Uninfo
from PIL import UnidentifiedImageError

from .config import EFFECT, EXCLUDEAI, MAX, SETU_PATH, SETU_R18, WITHDRAW_TIME, Config
from .cooldown import Cooldown
from .data_source import SetuHandler
from .database import (
    CooldownRecord,
    GroupWhiteListRecord,
    auto_upgrade_setuinfo,
    bind_message_data,
)
from .img_utils import EFFECT_FUNC_LIST, pil2bytes
from .models import Setu, SetuNotFindError
from .perf_timer import PerfTimer

# from .r18_whitelist import check_group_r18_whitelist
from .utils import SpeedLimiter

usage_msg = """TL;DR: 色图 或 看文档"""

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-setu-now",
    description="另一个色图插件",
    usage=usage_msg,
    type="application",
    homepage="https://github.com/kexue-z/nonebot-plugin-setu-now",
    config=Config,
    extra={},
)

global_speedlimiter = SpeedLimiter()

setu_matcher = on_alconna(
    Alconna(
        ["setu", "色图", "来点色图", "色色", "涩涩", "来点色色"],
        Args["num", int, 1],
        Args["key", str, ""],
        Option(
            "-r|--r18",
            action=action.store_true,
            default=False,
            help_text="是否获取R18内容",
        ),
        Option(
            "-t|--tag",
            Args["tag", str, ""],
            action=action.append,
            help_text="标签, 多个标签需要连续使用 -t aaa -t bbb 分隔",
        ),
        Option(
            "--switch",
            action=action.store_true,
            default=False,
            help_text="切换R18白名单",
        ),
        meta=CommandMeta(
            description=(
                "获取色图, 格式:\n"
                "setu [-r|--r18] [-t|--tag 标签] [--switch] [数量] [关键词]\n"
                "建议使用 -t 标签 来获取指定标签的色图，不建议使用关键词来获取色图。"
            )
        ),
    )
)


@setu_matcher.handle()
async def _(bot: Bot, session: Uninfo, result: Arparma):
    if not result.options.get("switch").value:
        return

    if session.user.id not in bot.config.superusers:
        await setu_matcher.finish("仅超级用户可以使用该功能")

    if not session.scene.is_group:
        await setu_matcher.finish("仅支持在群组中使用")

    has_r18_access = await GroupWhiteListRecord.get_record(session.group.id)
    if has_r18_access:
        await GroupWhiteListRecord.deactivate(session.group.id)
        await setu_matcher.finish("已关闭R18白名单")
    else:
        await GroupWhiteListRecord.activate(session.group.id, session.user.id)
        await setu_matcher.finish("已开启R18白名单")


@setu_matcher.handle()
async def handle_setu_command(
    session: Uninfo,
    result: Arparma,
    is_cooldown: bool = Depends(Cooldown),
):
    # is_cooldown: True 表示冷却完成
    if not is_cooldown:
        await UniMessage.text("你冲得太快啦，请稍后再试").send(reply_to=True)
        await setu_matcher.finish()

    await CooldownRecord.set_last_use_time(session.user.id)
    # 解析参数
    num = min(result.main_args.get("num", 1), MAX)
    key = result.main_args.get("key", "")
    r18 = result.options.get("r18").value if "r18" in result.options else False
    tag = (
        result.options.get("tag").args.get("tag", []) if "tag" in result.options else []
    )

    logger.debug(f"Setu: r18:{r18}, tag:{tag}, key:{key}, num:{num}")
    setu_total_timer = PerfTimer("Image request total")

    # 如果存在 tag 关键字, 则不用 key
    if tag:
        key = ""

    # R18内容控制逻辑
    if r18:
        has_r18_access = await _validate_r18_access(session)
        if not has_r18_access:
            await CooldownRecord.delete_record(session.user.id)
            await setu_matcher.finish(
                "不可以涩涩！\n本群未启用R18支持\n请移除R18标签或联系维护组"
            )
        num = 1  # R18模式下强制单张图片

    failure_msg = 0

    async def nb_send_handler(setu: Setu) -> None:
        nonlocal failure_msg
        if setu.img is None:
            logger.warning("Invalid image type, skipped")
            failure_msg += 1
            return

        for process_func in EFFECT_FUNC_LIST:
            if r18 and process_func == EFFECT_FUNC_LIST[0]:
                continue

            logger.debug(f"Using effect {process_func}")
            effert_timer = PerfTimer.start("Effect process")

            try:
                image = process_func(setu.img)  # type: ignore
            except UnidentifiedImageError:
                logger.warning(f"Unidentified image: {type(setu.img)}")
                failure_msg += 1
                return

            effert_timer.stop()

            msg = UniMessage.image(raw=pil2bytes(image))

            try:
                await global_speedlimiter.async_speedlimit()
                send_timer = PerfTimer("Image send")
                message_id = 0
                receipt = await msg.send()

                message_id = receipt.msg_ids[0]["message_id"]

                await auto_upgrade_setuinfo(setu)
                await bind_message_data(message_id, setu.pid)
                logger.debug(f"Message ID: {message_id}")

                if WITHDRAW_TIME:
                    logger.debug(
                        f"Recall message {message_id} in {WITHDRAW_TIME} seconds"
                    )
                    await receipt.recall(delay=WITHDRAW_TIME)

                send_timer.stop()
                global_speedlimiter.send_success()
                if SETU_PATH is None:  # 未设置缓存路径，删除缓存
                    Path(setu.img).unlink()
                return
            except ActionFailed:
                if not EFFECT:  # 设置不允许添加特效
                    failure_msg += 1
                    return
                await asyncio.sleep(0)
                logger.warning("Image send failed, retrying another effect")
        failure_msg += 1
        logger.warning("Image send failed after tried all effects")
        if SETU_PATH is None:  # 未设置缓存路径，删除缓存
            Path(setu.img).unlink()

    setu_handler = SetuHandler(key, tag, r18, num, nb_send_handler, EXCLUDEAI)
    try:
        await setu_handler.process_request()
    except SetuNotFindError:
        await setu_matcher.finish(f"没有找到关于 {tag or key} 的色图喵")
    if failure_msg:
        await setu_matcher.send(
            message=UniMessage.text(f"{failure_msg} 张图片消失了喵"),
        )

    if failure_msg == num:
        await CooldownRecord.delete_record(session.user.id)

    setu_total_timer.stop()


async def _validate_r18_access(session: Uninfo) -> bool:
    """验证R18内容访问权限"""
    # 如果是私聊，检查是否开启了R18权限
    if session.scene.is_private:
        return SETU_R18

    # 检查群是否在 R18 白名单中
    if session.scene.is_group:
        has_r18_access = await GroupWhiteListRecord.get_record(session.group.id)
        return True if has_r18_access else False

    return False


# TODO: 没有查询功能了，到时候再写
"""
setuinfo_matcher = on_command("信息")


@setuinfo_matcher.handle()
async def _(
    event: MessageEvent,
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

    if message_info := await MessageInfo.get_or_none(message_id=reply_message_id):
        message_pid = message_info.pid
    else:
        await setuinfo_matcher.finish("未找到该插画相关信息")

    if setu_info := await SetuInfo.get_or_none(pid=message_pid):
        info_message = MessageSegment.text(f"标题：{setu_info.title}\n")
        info_message += MessageSegment.text(f"画师：{setu_info.author}\n")
        info_message += MessageSegment.text(f"PID：{setu_info.pid}")

        await setu_matcher.finish(MessageSegment.reply(reply_message_id) + info_message)
    else:
        await setuinfo_matcher.finish("该插画相关信息已被移除")
"""
