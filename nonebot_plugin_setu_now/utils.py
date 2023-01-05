import time
import asyncio
from typing import List, Union, Optional

from httpx import AsyncClient
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import Bot, Message, GroupMessageEvent

from .config import SEND_INTERVAL
from .perf_timer import PerfTimer

try:
    import nonebot_plugin_localstore as store
except ImportError:
    from .. import nonebot_plugin_localstore as store


async def download_pic(
    url: str, proxies: Optional[str] = None, file_mode=False, file_name=""
) -> Union[bytes, str]:
    headers = {
        "Referer": "https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    }
    download_timer = PerfTimer.start("Image download")
    image_path = store.get_cache_file("nonebot_plugin_setu_now", file_name)
    async with AsyncClient().stream(method="GET", url=url, headers=headers, timeout=15, params=[("proxies", proxies)]) as response:  # type: ignore
        with open(image_path, "wb") as f:
            async for chunk in response.aiter_bytes():
                f.write(chunk)
    await response.aclose()
    download_timer.stop()
    return image_path
    # re = await client.get(url=url, headers=headers, timeout=60)
    download_timer.stop()
    # if re.status_code == 200:
    #     logger.debug("成功获取图片")
    #     return re.content
    # else:
    #     logger.error(f"获取图片失败: {re.status_code}")
    #     return


async def send_forward_msg(
    bot: Bot,
    event: GroupMessageEvent,
    name: str,
    uin: str,
    msgs: List[Message],
):
    """
    :说明: `send_forward_msg`
    > 发送合并转发消息

    :参数:
      * `bot: Bot`: bot 实例
      * `event: GroupMessageEvent`: 群聊事件
      * `name: str`: 名字
      * `uin: str`: qq号
      * `msgs: List[Message]`: 消息列表
    """

    def to_json(msg: Message):
        return {"type": "node", "data": {"name": name, "uin": uin, "content": msg}}

    messages = [to_json(msg) for msg in msgs]
    await bot.call_api(
        "send_group_forward_msg", group_id=event.group_id, messages=messages
    )


class SpeedLimiter:
    def __init__(self) -> None:
        self.send_success_time = 0

    def send_success(self) -> None:
        self.send_success_time = time.time()

    async def async_speedlimit(self):
        if (delay_time := time.time() - self.send_success_time) < SEND_INTERVAL:
            delay_time = round(delay_time, 2)
            logger.debug(f"Speed limit: Asyncio sleep {delay_time}s")
            await asyncio.sleep(delay_time)
