from nonebot_plugin_orm import Model, get_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from .data_source import SETU_SIZE, Setu


class SetuInfo(Model):
    pid: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str]
    title: Mapped[str]
    url: Mapped[str]


async def auto_upgrade_setuinfo(setu_instance: Setu):
    async with get_session() as session:
        session: AsyncSession
        result = await session.get(SetuInfo, int(setu_instance.pid))
        created = False
        if not result:
            result = SetuInfo(
                pid=int(setu_instance.pid),
                author=setu_instance.author,
                title=setu_instance.title,
                url=setu_instance.urls[SETU_SIZE],
            )
            session.add(result)
            await session.commit()
            await session.refresh(result)
            created = True
        return result, created


class MessageInfo(Model):
    message_id: Mapped[int] = mapped_column(primary_key=True)
    pid: Mapped[int]


async def bind_message_data(message_id: int, pid: int):
    async with get_session() as session:
        session: AsyncSession
        result = await session.get(MessageInfo, message_id)
        created = False
        if not result:
            result = MessageInfo(
                message_id=message_id,
                pid=pid,
            )
            session.add(result)
            await session.commit()
            await session.refresh(result)
            created = True
        return result, created


class GroupWhiteListRecord(Model):
    group_id: Mapped[int] = mapped_column(primary_key=True)
    operator_user_id: Mapped[int]
