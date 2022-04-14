from asyncio import gather
from typing import Optional

from httpx import AsyncClient

from .setu_class import SetuApiData
from .utils import download_pic


class Setu:
    def __init__(
        self,
        size: str = "regular",
        api_url: str = "https://api.lolicon.app/setu/v2",
        reverse_proxy_url: str = "i.pixiv.re",
        save: Optional[str] = None,
        proxy: Optional[str] = None,
    ):
        """初始化

        Args:
            size (str, optional): 图像大小. Defaults to "regular".
            api_url (str, optional): api地址. Defaults to "https://api.lolicon.app/setu/v2".
            reverse_proxy_url (str, optional): 图片反向代理地址. Defaults to "i.pixiv.re".
            save (Optional[str], optional): 是否保存. None 表示不保存 WebDAV 表示保存到WebDAV服务器, local 表示保存到本地. 默认 None 不保存.
            proxy (Optional[str], optional): 代理地址. 是否使用代理, 用于 api 请求和图片下载. Defaults to None.
        """
        self.size = size
        self.api_url = api_url
        self.reverse_proxy_url = reverse_proxy_url
        self.save = save
        self.proxy = proxy

    async def get_setu(
        self,
        keyword: Optional[str] = None,
        tags: Optional[list] = None,
        r18: bool = False,
        num: int = 1,
    ) -> "SetuApiData":
        data = await self._get_info_from_setu_api(keyword, tags, r18, num)

        return await self._download_img_from_reverse_proxy(data)

    async def _get_info_from_setu_api(
        self,
        keyword: Optional[str] = None,
        tags: Optional[list] = None,
        r18: bool = False,
        num: int = 1,
    ) -> "SetuApiData":
        data = {
            "keyword": keyword,
            "tags": tags,
            "r18": r18,
            "proxy": self.reverse_proxy_url,
            "num": num,
            "size": self.size,
        }
        headers = {"Content-Type": "application/json"}

        async with AsyncClient(proxies=self.proxy) as client:  # type: ignore
            res = await client.post(
                self.api_url, data=data, headers=headers, timeout=60
            )

        return SetuApiData(**res.json())

    async def _download_img_from_reverse_proxy(
        self,
        data: SetuApiData,
    ) -> "SetuApiData":
        tasks = []
        for setu in data.data:
            tasks.append(download_pic(setu.urls[self.size]))
        results = await gather(*tasks)
        for i in range(len(data.data)):
            data.data[i].img = results[i]
        return data

    def save_img(self):
        pass
