import asyncio
from typing import Callable

from wcferry import WxMsg

from function.yuanshen.function.auto_bbs.sign_handle import init_db, on_sign, off_sign, mhy_bbs_sign
from function.yuanshen.function.auto_bbs.coin_handle import mhy_bbs_coin

from database import cache

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
    if asyncio.run(cache.get(f'{msg.sender}_ys_sign')):    # 如果有缓存则提示等待
        func_send_text_msg(f'执行米有社原神签到中~\n请耐心等待反馈或3分钟后重试！', msg.roomid, msg.sender)
        return
    asyncio.run(cache.set(key=f'{msg.sender}_ys_sign', value='1', ttl=180))  # 设置一个三分钟的缓存
    _, send_msg = asyncio.run(mhy_bbs_sign(msg.sender))
    asyncio.run(cache.delete(f'{msg.sender}_ys_sign'))      # 执行后把缓存删掉
    func_send_text_msg(send_msg, msg.roomid, msg.sender)


def mhyBbsCoin(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    米游社手动获取米游币
    :param func_send_text_msg: 文本发送消息方法
    :param msg: 微信消息结构体
    :return: None
    """
    if asyncio.run(cache.get(f'{msg.sender}_get_myb')):    # 如果有缓存则提示等待
        func_send_text_msg(f'米游币获取中~\n请耐心等待反馈或3分钟后重试！', msg.roomid, msg.sender)
        return
    asyncio.run(cache.set(key=f'{msg.sender}_get_myb', value='1', ttl=180))
    send_msg = asyncio.run(mhy_bbs_coin(msg.sender))
    asyncio.run(cache.delete(f'{msg.sender}_get_myb'))     # 执行后把缓存删掉
    func_send_text_msg(send_msg, msg.roomid, msg.sender)
