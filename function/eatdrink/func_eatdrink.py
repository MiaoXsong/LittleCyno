import asyncio
import os
import random
from typing import Callable

from wcferry import WxMsg

from configuration import Config
from pathlib import Path

from database import cache

robot_name = Config().ROBOT_NAME

# 创建一个Path对象
current_file_path = Path(__file__)
# 获取当前文件所在的目录上级目录
current_dir_path = current_file_path.parent

# 今天吃什么路径
img_eat_path = current_dir_path / "eat_pic"
all_file_eat_name = os.listdir(str(img_eat_path))

# 今天喝什么路径
img_drink_path = current_dir_path / "drink_pic"
all_file_drink_name = os.listdir(str(img_drink_path))

# 上限回复消息
max_eat_msg = (
    "你已经吃的够多了！不许再吃了！",
    "吃吃吃，就知道吃，你都吃饱了！去运动一会儿再来！",
    "你猜我会不会再给你发好吃的图片！",
    f"没得吃的了！{robot_name}的食物都被你这坏蛋吃光了！",
    "你在等我给你发好吃的？做梦哦！你都吃那么多了，不许再吃了！"
)

max_drink_msg = (
    "你已经喝的够多了！不许再喝了！",
    "喝喝喝，就知道喝，你都喝胖了！去运动一会儿再来！",
    "你猜我会不会再给你发好喝的图片！",
    f"没得喝的了！{robot_name}的饮品都被你这坏蛋喝光了！",
    "你在等我给你发好喝的？做梦哦！你都喝那么多了，不许再喝了！"
)


def what_to_eat(func_send_text_msg: Callable[[str, str, str], None],
                func_send_img_msg: Callable[[str, str], None],
                msg: WxMsg) -> None:
    send_img = ''
    eat = random.choice(all_file_eat_name)
    cache_value = asyncio.run(cache.get(f'{msg.sender}_eat', ttl=600))
    if cache_value:
        if cache_value == 1:
            asyncio.run(cache.set(key=f'{msg.sender}_eat', value=2))  # 更新缓存
            send_msg = f"{robot_name}感觉你还是吃【{str(eat).split('.')[0]}】比较好"
            send_img = img_eat_path / eat
        else:
            send_msg = random.choice(max_eat_msg)
    else:
        asyncio.run(cache.set(key=f'{msg.sender}_eat', value=1))  # 设置缓存
        send_msg = f"{robot_name}建议你吃【{str(eat).split('.')[0]}】"
        send_img = img_eat_path / eat

    func_send_text_msg(send_msg, msg.roomid, msg.sender)
    if send_img:
        func_send_img_msg(str(send_img), msg.roomid)


def what_to_drink(func_send_text_msg: Callable[[str, str, str], None],
                  func_send_img_msg: Callable[[str, str], None],
                  msg: WxMsg) -> None:
    send_img = ''
    drink = random.choice(all_file_drink_name)
    cache_value = asyncio.run(cache.get(f'{msg.sender}_drink', ttl=600))
    if cache_value:
        if cache_value == 1:
            asyncio.run(cache.set(key=f'{msg.sender}_drink', value=2))  # 更新缓存
            send_msg = f"{robot_name}感觉你还是喝【{str(drink).split('.')[0]}】比较好"
            send_img = img_drink_path / drink
        else:
            send_msg = random.choice(max_drink_msg)
    else:
        asyncio.run(cache.set(key=f'{msg.sender}_drink', value=1))  # 设置缓存
        send_msg = f"{robot_name}建议你喝【{str(drink).split('.')[0]}】"
        send_img = img_drink_path / drink

    func_send_text_msg(send_msg, msg.roomid, msg.sender)
    if send_img:
        func_send_img_msg(str(send_img), msg.roomid)
