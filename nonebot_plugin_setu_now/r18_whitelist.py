from typing import List, Union
from pathlib import Path

from nonebot.plugin.on import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters.onebot.v11.event import GroupMessageEvent

WHITELIST_FILE_PATH = Path(__file__).parent.joinpath("whitelist.txt")


class GroupWhiteListChecker:
    def __init__(self) -> None:
        self.whitelist_group_id: List[int] = []

    def check_is_group_in_whitelist(self, group_id: int) -> bool:
        return group_id in self.whitelist_group_id

    def whitelist_add(self, group_id: int) -> None:
        if self.check_is_group_in_whitelist(group_id):
            return
        self.whitelist_group_id.append(group_id)

    def whitelist_del(self, group_id: int) -> None:
        if not self.check_is_group_in_whitelist(group_id):
            return
        self.whitelist_group_id.pop(self.whitelist_group_id.index(group_id))

    def load(self) -> None:
        with open(WHITELIST_FILE_PATH, "r") as f:
            self.whitelist_group_id = list(
                map(lambda i: int(i) if i else 0, f.read().split("\n"))
            )

    def save(self) -> None:
        with open(WHITELIST_FILE_PATH, "w") as f:
            f.write("\n".join(map(str, self.whitelist_group_id)))


group_r18_whitelist_checker = GroupWhiteListChecker()
group_r18_whitelist_checker.load()

r18_activate_matcher = on_command(
    "开启涩涩", aliases={"可以涩涩", "r18开启"}, permission=SUPERUSER
)


@r18_activate_matcher.handle()
async def _(event: GroupMessageEvent):
    group_r18_whitelist_checker.whitelist_add(event.group_id)
    await r18_activate_matcher.finish("已解除本群R18限制")


r18_deactivate_matcher = on_command(
    "关闭涩涩", aliases={"不可以涩涩", "r18关闭"}, permission=SUPERUSER
)


@r18_deactivate_matcher.handle()
async def _(event: GroupMessageEvent):
    group_r18_whitelist_checker.whitelist_del(event.group_id)
    await r18_deactivate_matcher.finish("已启用本群R18限制")
