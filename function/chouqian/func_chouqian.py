import asyncio
from typing import Callable

from wcferry import WxMsg

from function.chouqian.get_qianwen import get_qianwen_by_web, get_qianwen_by_local
from function.chouqian.chouqian import chou_qian, jieqian, init_db, clear_user_table


def getQianwenByWeb() -> None:
    """
    开发的时候去网站爬签文数据
    之后会通过sql文件直接导入数据，不需要爬取了
    运行完成后会有警告，但是不影响使用
    :return: None
    """
    asyncio.run(get_qianwen_by_web())


def getQianwenByLocal() -> None:
    """
    使用sql文件导入签文数据
    :return:
    """
    asyncio.run(get_qianwen_by_local())


def chouQian(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    抽签
    :param func_send_text_msg: 文本消息回复方法
    :param msg: 微信消息结构
    :return: None
    """
    asyncio.run(chou_qian(send_txt_msg=func_send_text_msg, user_id=msg.sender, group_id=msg.roomid))


def jieQian(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    解签
    :param func_send_text_msg: 文本消息回复方法
    :param msg: 微信消息结构
    :return: None
    """
    asyncio.run(jieqian(send_txt_msg=func_send_text_msg, user_id=msg.sender, group_id=msg.roomid))


def initUserTable() -> None:
    """
    创建抽签用户表
    :return: None
    """
    asyncio.run(init_db())


def clearUserTable() -> None:
    """
    清空抽签用户表
    :return: None
    """
    asyncio.run(clear_user_table())


# if __name__ == '__main__':
#     # getQianwenByWeb()
#     getQianwenByLocal()
#     # clearUserTable()
