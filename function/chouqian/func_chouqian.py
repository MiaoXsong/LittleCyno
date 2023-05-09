import asyncio

from wcferry import WxMsg

from function.chouqian.get_qianwen import get_qianwen_by_web, get_qianwen_by_local
from function.chouqian.chouqian import chou_qian, jieqian, init_db


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


def chouQian(msg: WxMsg) -> str:
    """
    抽签
    :param msg: 微信消息结构
    :return: None
    """
    return asyncio.run(chou_qian(msg))


def jieQian(msg: WxMsg) -> str:
    """
    解签
    :param msg: 微信消息结构
    :return: None
    """
    return asyncio.run(jieqian(msg))


def initUserDB() -> None:
    """
    创建抽签用户表
    :return: None
    """
    asyncio.run(init_db())


if __name__ == '__main__':
    # getQianwenByWeb()
    getQianwenByLocal()
