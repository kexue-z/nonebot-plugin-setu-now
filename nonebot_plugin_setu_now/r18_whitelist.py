from typing import Optional

from nonebot.log import logger
from nonebot.plugin.on import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11 import MessageEvent, GroupMessageEvent

from .database import GroupWhiteListRecord


async def get_group_white_list_record(
    event: MessageEvent,
) -> Optional[GroupWhiteListRecord]:
    if isinstance(event, GroupMessageEvent):
        res = await GroupWhiteListRecord.get_or_none(group_id=event.group_id)
        logger.debug(f"Database white list record: {res}")
        return res


r18_activate_matcher = on_command(
    "开启涩涩", aliases={"可以涩涩", "开启色色", "可以色色", "r18开启"}, permission=SUPERUSER
)


@r18_activate_matcher.handle()
async def _(event: GroupMessageEvent):
    if _ := await GroupWhiteListRecord.get_or_none(group_id=event.group_id):
        logger.debug("已有白名单记录")

    else:
        logger.debug(f"添加白名单 {event.group_id}")
        await GroupWhiteListRecord.create(
            group_id=event.group_id, operator_user_id=event.user_id
        )

    await r18_activate_matcher.finish("已解除本群涩图限制")


r18_deactivate_matcher = on_command(
    "关闭涩涩", aliases={"不可以涩涩", "关闭色色", "不可以色色", "r18关闭"}, permission=SUPERUSER
)


@r18_deactivate_matcher.handle()
async def _(event: GroupMessageEvent):
    if record := await GroupWhiteListRecord.get_or_none(group_id=event.group_id):
        logger.debug(f"删除白名单 {event.group_id}")
        await record.delete()
        await record.save()

    await r18_deactivate_matcher.finish("已关闭本群涩图限制")
