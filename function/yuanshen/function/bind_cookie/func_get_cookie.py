import asyncio
from wcferry import WxMsg

from function.yuanshen.function.bind_cookie.get_cookie import init_db, generate_login_data, check_qrcode


def initCookieTable() -> None:
    """
    初始化cookie表 以及 查询记录表
    :return: None
    """
    asyncio.run(init_db())


def generateLoginData(func_send_text_msg, func_send_img_msg, robot_name, msg: WxMsg) -> None:
    """
    创建并发送登陆二维码
    :param func_send_text_msg: 文本消息发送方法
    :param func_send_img_msg: 图片消息发送方法
    :param robot_name: 机器人名称
    :param msg: 微信消息结构体
    :return: None
    """
    asyncio.run(generate_login_data(func_send_text_msg, func_send_img_msg,
                                    robot_name, msg.sender, msg.roomid))


def checkQrcode(func_send_text_msg) -> None:
    """
    检查扫码登陆情况
    :param func_send_text_msg: 文本消息发送方法
    :return: None
    """
    asyncio.run(check_qrcode(send_txt_msg=func_send_text_msg))
