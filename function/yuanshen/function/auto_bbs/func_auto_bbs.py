import asyncio
from typing import Callable

from wcferry import WxMsg

from function.yuanshen.function.auto_bbs.sign_handle import init_db, on_sign, off_sign, mhy_bbs_sign


def initSignUserTable() -> None:
    """
    创建签到用户表
    :return: None
    """
    asyncio.run(init_db())


def onSign(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    开启米有社原神定时签到
    :param func_send_text_msg: 文本发送消息方法
    :param msg: 微信消息结构体
    :return: None
    """
    asyncio.run(on_sign(send_txt_msg=func_send_text_msg,
                        user_id=msg.sender, group_id=msg.roomid))


def offSign(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    关闭米有社定时签到
    :param func_send_text_msg: 文本发送消息方法
    :param msg: 微信消息结构体
    :return: None
    """
    asyncio.run(off_sign(send_txt_msg=func_send_text_msg,
                         user_id=msg.sender, group_id=msg.roomid))


def mhyBbsSign(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    米游社原神手动签到
    :param func_send_text_msg: 文本发送消息方法
    :param msg: 微信消息结构体
    :return: None
    """
    _, send_msg = asyncio.run(mhy_bbs_sign(msg.sender))
    func_send_text_msg(send_msg, msg.roomid, msg.sender)
