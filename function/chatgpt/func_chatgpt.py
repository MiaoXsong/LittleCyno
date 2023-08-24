import asyncio
from function.chatgpt.chatgpt import get_answer, del_contextual_content, get_contextual_content
from datetime import datetime
from typing import Callable
from wcferry import WxMsg
from configuration import Config

robot_name = Config().ROBOT_NAME


def chatGpt(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    time_start = datetime.now()  # 记录开始时间
    answer = asyncio.run(get_answer(question=msg.content, wxid=msg.sender))
    func_send_text_msg(answer, msg.roomid, msg.sender)
    time_end = datetime.now()  # 记录结束时间
    time_consuming = round((time_end - time_start).total_seconds(), 2)

    tips = f"本次回答耗时：{time_consuming}s\n" \
           f"提问支持上下文关联，最高可存储{Config().CHATGPT_CONTEXTS}条记录\n" \
           f"发送【{robot_name}查看上下文】可查看当前存储的个人上下文记录\n" \
           f"发送【{robot_name}清除上下文】可清除当前存储的个人上下文记录"
    func_send_text_msg(tips, msg.roomid, msg.sender)


def delContextualContent(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    answer = asyncio.run(del_contextual_content(msg.sender))
    func_send_text_msg(answer, msg.roomid, msg.sender)


def getContextualContent(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    answer = asyncio.run(get_contextual_content(msg.sender))
    func_send_text_msg(answer, msg.roomid, msg.sender)
