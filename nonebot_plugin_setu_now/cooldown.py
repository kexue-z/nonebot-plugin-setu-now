"""
CD 管理
"""

from nonebot import Bot, logger
from nonebot_plugin_uninfo import Uninfo

from .config import CDTIME
from .database import CooldownRecord


async def Cooldown(bot: Bot, session: Uninfo) -> bool:
    """检查用户是否在冷却中

    超级管理员可以忽略冷却时间

    Args:
        session: 会话信息

    Returns:
        bool: 是否在冷却中（True表示冷却完成，False表示还在冷却中）
    """
    user_id = session.user.id

    if session.user.id in bot.config.superusers:
        logger.debug("Superuser ignore cooldown")
        return True

    return await CooldownRecord.check_is_cooldown(user_id, cd=CDTIME)
