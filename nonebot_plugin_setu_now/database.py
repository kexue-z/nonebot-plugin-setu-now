from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from .models import SetuInfo, MessageInfo
from .data_source import SETU_SIZE, Setu


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
