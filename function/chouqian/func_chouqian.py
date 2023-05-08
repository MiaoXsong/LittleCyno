import asyncio

from get_qianwen import get_qianwen_by_web_main, get_qianwen_by_local


def getQianwenByWeb() -> None:
    """
    开发的时候去网站爬签文数据
    之后会通过sql文件直接导入数据，不需要爬取了
    :return: None
    """
    asyncio.run(get_qianwen_by_web_main())


def getQiqnwenByLocal() -> None:
    """
    使用sql文件导入签文数据
    :return:
    """
    asyncio.run(get_qianwen_by_local())


if __name__ == '__main__':
    # getQianwenByWeb()
    getQiqnwenByLocal()
