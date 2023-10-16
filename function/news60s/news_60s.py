import asyncio
import time
from typing import Callable, List
from datetime import datetime

import aiohttp
import aiofiles

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


async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                raise Exception(f"Failed to fetch image. Status code: {response.status}")


async def save_image(img_bytes, file_path):
    async with aiofiles.open(file_path, mode='wb') as file:
        await file.write(img_bytes)


async def send_60s_img(send_img_msg: Callable[[str, str], None],
                       send_text_msg: Callable[[str, str, str], None], groups: List) -> None:
    timestamp = time.time()
    img_name = f'{timestamp}.png'
    image_url = 'https://api.03c3.cn/zb/'
    img_tmp_path = tmp_path / img_name

    try:
        logger.debug("正在获取图片")
        img_bytes = await fetch_image(image_url)
        logger.debug("正在保存图片")
        await save_image(img_bytes, img_tmp_path)
    except Exception as e:
        logger.error(f"Error: {e}")

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
    try:
        os.remove(img_tmp_path)  # 发完后删掉
    except Exception as e:
        logger.error(f"Error: {e}")
