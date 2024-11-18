from typing import List, Callable
from asyncio import gather
from pathlib import Path

import nonebot_plugin_localstore as store
from httpx import AsyncClient
from nonebot.log import logger

from .utils import download_pic
from .config import PROXY, API_URL, SETU_SIZE, REVERSE_PROXY
from .models import Setu, SetuApiData, SetuNotFindError

CACHE_PATH = Path(store.get_cache_dir("nonebot_plugin_setu_now"))
if not CACHE_PATH.exists():
    logger.info("Creating setu cache floder")
    CACHE_PATH.mkdir(parents=True, exist_ok=True)


class SetuHandler:
    def __init__(
        self, key: str, tags: List[str], r18: bool, num: int, handler: Callable, excludeAI: bool = False
    ) -> None:
        self.key = key
        self.tags = tags
        self.r18 = r18
        self.num = num
        self.api_url = API_URL
        self.size = SETU_SIZE
        self.proxy = PROXY
        self.reverse_proxy_url = REVERSE_PROXY
        self.handler = handler
        self.setu_instance_list: List[Setu] = []
        self.excludeAI = excludeAI

    async def refresh_api_info(self):
        data = {
            "keyword": self.key,
            "tag": self.tags,
            "r18": self.r18,
            "proxy": self.reverse_proxy_url,
            "num": self.num,
            "size": self.size,
            "excludeAI" : self.excludeAI
        }
        headers = {"Content-Type": "application/json"}

        async with AsyncClient(proxies=self.proxy) as client:  # type: ignore
            res = await client.post(
                self.api_url, json=data, headers=headers, timeout=60
            )
        data = res.json()
        setu_api_data_instance = SetuApiData(**data)
        if len(setu_api_data_instance.data) == 0:
            raise SetuNotFindError()
        logger.debug(f"API Responsed {len(setu_api_data_instance.data)} image")
        for i in setu_api_data_instance.data:
            self.setu_instance_list.append(Setu(data=i))

    async def prep_handler(self, setu: Setu):
        setu.img = await download_pic(
            url=setu.urls[SETU_SIZE],
            proxies=self.proxy,
            file_mode=True,
            file_name=f"{setu.pid}.{setu.ext}",
        )
        await self.handler(setu)

    async def process_request(self):
        await self.refresh_api_info()
        task_list = []
        for i in self.setu_instance_list:
            task_list.append(self.prep_handler(i))
        await gather(*task_list)
