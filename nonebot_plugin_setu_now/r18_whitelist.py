from typing import List, Union
from pathlib import Path

from nonebot import get_driver
from sqlmodel import select
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.plugin.on import on_command
from nonebot.permission import SUPERUSER
from sqlmodel.ext.asyncio.session import AsyncSession
from nonebot.adapters.onebot.v11.event import GroupMessageEvent

try:
    from nonebot_plugin_datastore import get_session
except ModuleNotFoundError:
    from ..nonebot_plugin_datastore import get_session

from .models import GroupWhiteListRecord


async def get_group_white_list_record(
    event: GroupMessageEvent, db_session: AsyncSession = Depends(get_session)
):
    statement = select(GroupWhiteListRecord).where(
        GroupWhiteListRecord.group_id == event.group_id
    )
    result = await db_session.exec(statement)
    result = result.first()
    logger.debug(f"Database white list record: {result}")
    return result


r18_activate_matcher = on_command(
    "开启涩涩", aliases={"可以涩涩", "r18开启"}, permission=SUPERUSER
)


@r18_activate_matcher.handle()
async def _(event: GroupMessageEvent, db_session: AsyncSession = Depends(get_session)):
    db_session.add(
        GroupWhiteListRecord(
            group_id=int(event.group_id), operator_user_id=int(event.user_id)
        )
    )
    await db_session.commit()
    await r18_activate_matcher.finish("已解除本群涩图限制")


r18_deactivate_matcher = on_command(
    "关闭涩涩", aliases={"不可以涩涩", "r18关闭"}, permission=SUPERUSER
)


@r18_deactivate_matcher.handle()
async def _(
    record=Depends(get_group_white_list_record),
    db_session: AsyncSession = Depends(get_session),
):
    if record is None:
        await r18_deactivate_matcher.finish("已启用本群涩图限制")
    await db_session.delete(record)
    await db_session.commit()
    await r18_deactivate_matcher.finish("已启用本群涩图限制")
