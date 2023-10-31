import asyncio
import re

from function.chatgpt.chatgpt import get_answer, del_contextual_content, get_contextual_content
from datetime import datetime
from typing import Callable
from wcferry import WxMsg
from configuration import Config
from database import cache

robot_name = Config().ROBOT_NAME


def chatGpt(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    result = True
    cache_value = asyncio.run(cache.get(f'{msg.sender}_chatgpt', ttl=300))  # 获取缓存

    if str(msg.content).strip().startswith(robot_name):  # 如果消息以配置文件自定义的机器人名称开头, 则把机器人开头名称去掉
        question = str(msg.content).split(robot_name)[-1]
    else:  # 否则就取@符号后面的文字
        question = re.sub(r"@.*?[\u2005|\s]", "", msg.content).replace(" ", "")
    if cache_value:
        tips = f"你的上个问题我还没想好呢，等我先把上个问题回答了再问吧~"
        func_send_text_msg(tips, msg.roomid, msg.sender)
    else:
        asyncio.run(cache.set(key=f'{msg.sender}_chatgpt', value=1))  # 设置缓存
        time_start = datetime.now()  # 记录开始时间
        answer, result = asyncio.run(get_answer(question=question, wxid=msg.sender))
        func_send_text_msg(answer, msg.roomid, msg.sender)
        time_end = datetime.now()  # 记录结束时间
        time_consuming = round((time_end - time_start).total_seconds(), 2)
        asyncio.run(cache.delete(key=f'{msg.sender}_chatgpt'))  # 删除缓存
    #     tips = f"本次回答耗时：{time_consuming}s\n" \
    #            f"提问支持上下文关联，最高可存储{Config().CHATGPT_CONTEXTS}条记录\n" \
    #            f"发送【{robot_name}查看上下文】可查看当前个人存储的记录\n" \
    #            f"发送【{robot_name}清除上下文】可清除当前个人存储的记录"
    # if result:
    #     func_send_text_msg(tips, msg.roomid, msg.sender)


def delContextualContent(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    answer = asyncio.run(del_contextual_content(msg.sender))
    func_send_text_msg(answer, msg.roomid, msg.sender)


def getContextualContent(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    answer = asyncio.run(get_contextual_content(msg.sender))
    func_send_text_msg(answer, msg.roomid, msg.sender)
