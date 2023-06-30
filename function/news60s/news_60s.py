import asyncio
import time
from typing import Callable, List
from datetime import datetime
from function.yuanshen.utils.requests import aiorequests
from pathlib import Path
import os

from logger.logger_object import news_60s_logger

logger = news_60s_logger

current_file_path = Path(__file__)
current_dir_path = current_file_path.parent
tmp_path = current_dir_path / "tmp"
if not os.path.exists(tmp_path):
    logger.debug("创建tmp文件夹")
    os.makedirs(tmp_path)


async def send_60s_img(send_img_msg: Callable[[str, str], None],
                       send_text_msg: Callable[[str, str, str], None], groups: List) -> None:
    timestamp = time.time()
    img_name = f'{timestamp}.png'
    image_url = 'https://api.qqsuu.cn/api/dm-60s'
    logger.debug("正在获取图片")
    img = await aiorequests.get_img(image_url)
    img_tmp_path = tmp_path / img_name
    logger.debug("正在保存图片")
    img.save(img_tmp_path)

    logger.info("正在发送到所监控的群内")
    now = datetime.now()
    date_str = now.strftime('%Y年%m月%d日')
    msg = f'{date_str} 每天60秒读懂世界~'

    async def send_msg(room_id):
        send_text_msg(msg, room_id, '')
        send_img_msg(str(img_tmp_path), room_id)

    tasks = [send_msg(room_id) for room_id in groups]
    await asyncio.gather(*tasks)

    logger.info("发送完毕")
    os.remove(img_tmp_path)  # 发完后删掉
