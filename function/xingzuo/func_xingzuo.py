import asyncio
from typing import Literal, Callable

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
    :return: None
    """
    asyncio.run(init_xz_table())


def getXzDataByWeb(time: Literal['day', 'tomorrow']) -> None:
    """
    从web获取今天或明天的星座信息
    :param time: `day`表示获取今天的数据，`tomorrow`表示获取明天的数据
    :return: None
    """
    asyncio.run(get_xz_data_by_web(time))


def xingZuo(func_send_text_msg: Callable[[str, str, str], None], msg: WxMsg) -> None:
    """
    星座运势
    :param func_send_text_msg: 文本消息回复方法
    :param msg: 微信消息结构
    :return: None
    """
    xz_name = str(msg.content).split(robot_name)[-1]
    asyncio.run(xing_zuo(send_txt_msg=func_send_text_msg,
                         user_id=msg.sender,
                         group_id=msg.roomid,
                         xz_name=xz_name_dict[xz_name]))
