import asyncio
from typing import Literal

from function.xingzuo.get_data_by_web import init_xz_table, get_xz_data_by_web


def initXzTable() -> None:
    """
    初始化星座表
    :return:
    """
    asyncio.run(init_xz_table())


def getXzDataByWeb(time: Literal['day', 'tomorrow']) -> None:
    """
    从web获取今天或明天的星座信息
    :param time: `day`表示获取今天的数据，`tomorrow`表示获取明天的数据
    :return: None
    """
    asyncio.run(get_xz_data_by_web(time))
