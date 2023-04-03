from nonebot import require
from sqlalchemy import select
from nonebot.log import logger
from nonebot.params import Depends
from nonebot.plugin.on import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent
from sqlalchemy.ext.asyncio.session import AsyncSession

from .models import GroupWhiteListRecord

require("nonebot_plugin_datastore")

from nonebot_plugin_datastore import get_session


async def get_group_white_list_record(event: MessageEvent, db_session: AsyncSession = Depends(get_session)):
    if not isinstance(event, GroupMessageEvent):
        return None
    statement = select(GroupWhiteListRecord).where(GroupWhiteListRecord.group_id == event.group_id)
    result = (await db_session.scalars(statement)).first()  # type: ignore
    if not result:
        return None
    logger.debug(f"Database white list record: {result}")
    return result


r18_activate_matcher = on_command("开启涩涩", aliases={"可以涩涩", "r18开启"}, permission=SUPERUSER)


@r18_activate_matcher.handle()
async def _(
    event: GroupMessageEvent,
    db_session: AsyncSession = Depends(get_session),
    record=Depends(get_group_white_list_record),
):
    if not record:
        await r18_activate_matcher.finish("已解除本群涩图限制")
    db_session.add(GroupWhiteListRecord(group_id=int(event.group_id), operator_user_id=int(event.user_id)))
    await db_session.commit()
    await r18_activate_matcher.finish("已解除本群涩图限制")


r18_deactivate_matcher = on_command("关闭涩涩", aliases={"不可以涩涩", "r18关闭"}, permission=SUPERUSER)


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
