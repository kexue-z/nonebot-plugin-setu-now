import datetime
import time

from nonebot import get_driver, require

# from nonebot_plugin_apscheduler import scheduler
from nonebot.adapters.onebot.v11 import Bot
from nonebot.log import logger
from .config import Config

scheduler = require("nonebot_plugin_apscheduler").scheduler

WITHDRAW_TIME = Config.parse_obj(get_driver().config.dict()).setu_withdraw


def add_withdraw_job(bot: Bot, message_id: int):
    if WITHDRAW_TIME:
        logger.debug("添加撤回任务")
        scheduler.add_job(
            withdraw_msg,
            "date",
            args=[bot, message_id],
            run_date=datetime.datetime.fromtimestamp(time.time() + WITHDRAW_TIME),  # type: ignore
        )


async def withdraw_msg(bot: Bot, message_id: int):
    await bot.delete_msg(message_id=message_id)
