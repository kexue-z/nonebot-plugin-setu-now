"""
TODO: 白名单

"""

from typing import Optional

from nonebot.adapters.onebot.v11.event import GroupMessageEvent, MessageEvent
from nonebot.log import logger
from nonebot.permission import SUPERUSER
from nonebot.plugin.on import on_command
from nonebot_plugin_orm import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from .database import GroupWhiteListRecord


async def get_group_white_list_record(
    event: MessageEvent,
) -> Optional[GroupWhiteListRecord]:
    if isinstance(event, GroupMessageEvent):
        async with get_session() as session:
            session: AsyncSession
            res = await session.get(GroupWhiteListRecord, event.group_id)
            logger.debug(f"Database white list record: {res}")
            return res


r18_activate_matcher = on_command(
    "开启涩涩",
    aliases={"可以涩涩", "开启色色", "可以色色", "r18开启"},
    permission=SUPERUSER,
)


@r18_activate_matcher.handle()
async def _(event: GroupMessageEvent):
    async with get_session() as session:
        session: AsyncSession
        existing = await session.get(GroupWhiteListRecord, event.group_id)
        if existing:
            logger.debug("已有白名单记录")
        else:
            logger.debug(f"添加白名单 {event.group_id}")
            new_record = GroupWhiteListRecord(
                group_id=event.group_id, operator_user_id=event.user_id
            )
            session.add(new_record)
            await session.commit()

    await r18_activate_matcher.finish("已解除本群涩图限制")


r18_deactivate_matcher = on_command(
    "关闭涩涩",
    aliases={"不可以涩涩", "关闭色色", "不可以色色", "r18关闭"},
    permission=SUPERUSER,
)


@r18_deactivate_matcher.handle()
async def _(event: GroupMessageEvent):
    async with get_session() as session:
        session: AsyncSession
        record = await session.get(GroupWhiteListRecord, event.group_id)
        if record:
            logger.debug(f"删除白名单 {event.group_id}")
            await session.delete(record)
            await session.commit()

    await r18_deactivate_matcher.finish("已关闭本群涩图限制")
