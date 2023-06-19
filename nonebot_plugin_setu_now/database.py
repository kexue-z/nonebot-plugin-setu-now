from nonebot.plugin import require
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from .data_source import SETU_SIZE, Setu
from .models import GroupWhiteListRecord, MessageInfo, SetuInfo

require("nonebot_plugin_datastore")

from tortoise.models import Model
from tortoise import fields


async def auto_upgrade_setuinfo(session: AsyncSession, setu_instance: Setu):
    statement = select(SetuInfo).where(SetuInfo.pid == setu_instance.pid)
    setuinfo_result = (await session.scalars(statement)).first()  # type: ignore
    if setuinfo_result:
        return
    session.add(
        SetuInfo(
            pid=int(setu_instance.pid),
            author=setu_instance.author,
            title=setu_instance.title,
            url=setu_instance.urls[SETU_SIZE],
        )
    )
    await session.commit()


async def bind_message_data(session: AsyncSession, message_id: int, pid: int):
    session.add(
        MessageInfo(
            message_id=message_id,
            pid=pid,
        )
    )
    await session.commit()


class SetuInfo(Model):
    pid = fields.IntField(pk=True)
    author = fields.CharField(max_length=50)
    title = fields.CharField(max_length=50)
    url = fields.TextField()

    class Meta:
        table = "setu_info"


class MessageInfo(Model):
    message_id = fields.IntField(pk=True)
    pid = fields.IntField()

    class Meta:
        table = "message_data"


class GroupWhiteListRecord(Model):
    group_id = fields.IntField(pk=True)
    operator_user_id = fields.IntField()

    class Meta:
        table = "white_list"
