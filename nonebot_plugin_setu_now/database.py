from datetime import datetime

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
    group_id: Mapped[str] = mapped_column(primary_key=True)
    operator_user_id: Mapped[str]

    @classmethod
    async def activate(cls, group_id: str, operator_user_id: str) -> bool:
        """激活群白名单

        Args:
            group_id: 群号
            operator_user_id: 操作者用户ID

        Returns:
            bool: 是否成功激活（True表示激活成功，False表示已存在）
        """
        async with get_session() as session:
            session: AsyncSession
            record = await session.get(cls, group_id)
            if record:
                return False
            record = cls(group_id=group_id, operator_user_id=operator_user_id)
            session.add(record)
            await session.commit()
            return True

    @classmethod
    async def deactivate(cls, group_id: str) -> bool:
        """取消群白名单

        Args:
            group_id: 群号

        Returns:
            bool: 是否成功取消（True表示取消成功，False表示记录不存在）
        """
        async with get_session() as session:
            session: AsyncSession
            record = await session.get(cls, group_id)
            if not record:
                return False
            await session.delete(record)
            await session.commit()
            return True

    @classmethod
    async def get_record(cls, group_id: str) -> "GroupWhiteListRecord | None":
        """获取群白名单记录

        Args:
            group_id: 群号

        Returns:
            GroupWhiteListRecord | None: 白名单记录（存在返回记录，不存在返回None）
        """
        async with get_session() as session:
            session: AsyncSession
            return await session.get(cls, group_id)


class CooldownRecord(Model):
    """冷却时间记录表"""

    user_id: Mapped[str] = mapped_column(primary_key=True)
    last_use_time: Mapped[datetime]

    @classmethod
    async def check_is_cooldown(cls, user_id: str, cd: int) -> bool:
        """检测用户是否冷却完成

        Args:
            user_id: 用户ID
            cd: 冷却时间（秒）

        Returns:
            bool: 是否冷却完成（True表示冷却完成，False表示还在冷却中）
        """
        async with get_session() as session:
            session: AsyncSession
            record = await session.get(cls, user_id)

            if not record:
                return True

            # 检查是否超过冷却时间
            time_diff = datetime.now() - record.last_use_time
            return time_diff.total_seconds() >= cd

    @classmethod
    async def set_last_use_time(cls, user_id: str) -> None:
        """设置用户的上次使用时间

        Args:
            user_id: 用户ID
        """
        async with get_session() as session:
            session: AsyncSession
            record = await session.get(cls, user_id)

            if not record:
                # 创建新记录
                record = cls(user_id=user_id, last_use_time=datetime.now())
                session.add(record)
            else:
                # 更新现有记录
                record.last_use_time = datetime.now()

            await session.commit()

    @classmethod
    async def delete_record(cls, user_id: str) -> bool:
        """删除用户的冷却记录

        Args:
            user_id: 用户ID

        Returns:
            bool: 是否成功删除记录（True表示删除成功，False表示记录不存在）
        """
        async with get_session() as session:
            session: AsyncSession
            record = await session.get(cls, user_id)

            if not record:
                return False

            await session.delete(record)
            await session.commit()
            return True
