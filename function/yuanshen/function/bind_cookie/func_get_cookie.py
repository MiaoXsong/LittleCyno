import asyncio
from wcferry import WxMsg

from function.yuanshen.function.bind_cookie.get_cookie import init_db, generate_login_data, check_qrcode


def initCookieTable() -> None:
    asyncio.run(init_db())


def generateLoginData(func_send_text_msg, func_send_img_msg, robot_name, msg: WxMsg) -> None:
    asyncio.run(generate_login_data(func_send_text_msg, func_send_img_msg,
                                           robot_name, msg.sender, msg.roomid))


def checkQrcode(func_send_text_msg):
    asyncio.run(check_qrcode(send_txt_msg=func_send_text_msg))
