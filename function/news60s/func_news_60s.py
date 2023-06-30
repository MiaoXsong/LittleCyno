import asyncio
from configuration import Config

from typing import Callable
from function.news60s.news_60s import send_60s_img

send_groups = Config().GROUPS


def sendNews(func_send_img_msg: Callable[[str, str], None],
             func_send_text_msg: Callable[[str, str, str], None]) -> None:
    asyncio.run(send_60s_img(func_send_img_msg, func_send_text_msg, send_groups))
