from __future__ import annotations

import time
from typing import Dict

from nonebot.log import logger


class PerfTimer:
    timer_list: Dict[str, float] = {}

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.start_time: float = time.time()

    @classmethod
    def start(cls, name: str, output: bool = False):
        if output:
            logger.debug(f"{name} started")
        return cls(name)

    def stop(self):
        timer_count = time.time() - self.start_time
        timer_count = round(timer_count, 2)
        logger.debug(f"{self.name} took {timer_count}s")
