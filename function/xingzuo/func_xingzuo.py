import asyncio
from typing import Literal

from wcferry import WxMsg
from function.xingzuo.character import xz_name_dict
from function.xingzuo.get_data_by_web import init_xz_table, get_xz_data_by_web
from function.xingzuo.xingzuo import xing_zuo
from configuration import Config

config = Config()
robot_name = config.ROBOT_NAME


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


def xingZuo(msg: WxMsg) -> str:
    """
    星座运势
    :param xz_name: 星座的名称，例如 `tiancheng`
    :return: 机器人回复的消息
    """
    xz_name = str(msg.content).split(robot_name)[-1]
    return asyncio.run(xing_zuo(xz_name_dict[xz_name]))
