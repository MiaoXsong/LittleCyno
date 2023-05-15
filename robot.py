# -*- coding: utf-8 -*-

import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from wcferry import Wcf, WxMsg

from configuration import Config
from job_mgmt import Job
from logger.logger_object import robot_logger
from functools import partial


class Robot(Job):
    """个性化自己的机器人
    """

    def __init__(self, config: Config, wcf: Wcf) -> None:
        self.logger = robot_logger
        self.function_dict = {}
        self.wcf = wcf
        self.config = config
        self.robot_name = config.ROBOT_NAME
        self.groups = self.config.GROUPS

        self.wxid = self.wcf.get_self_wxid()
        self.allContacts = self.getAllContacts()
        self.load_function()

        self.logger.debug(f"机器人昵称：{self.robot_name}")
        self.logger.debug(f"监控的群：{self.groups}")

        current_file_path = Path(__file__)
        current_dir_path = current_file_path.parent
        self.temp_path = current_dir_path / "temp"
        if not os.path.exists(self.temp_path):
            os.makedirs(self.temp_path)

    def load_function(self) -> None:
        """
        根据配置文件的功能开关加载功能
        :return:
        """
        chouqian = self.config.CHOU_QIAN
        xingzuo = self.config.XING_ZUO
        yuanshen = self.config.YUAN_SHEN
        self.logger.debug(f"抽签开关：{chouqian}")

        if str(chouqian).lower() == 'on':
            self.logger.info(f"正在加载抽签功能")
            from function import chouqian
            self.function_dict["抽签"] = partial(chouqian.func_chouqian.chouQian, func_send_text_msg=self.sendTextMsg)
            self.function_dict["解签"] = partial(chouqian.func_chouqian.jieQian, func_send_text_msg=self.sendTextMsg)
            self.onEveryTime("00:00", chouqian.func_chouqian.clearUserTable)
        if str(xingzuo).lower() == 'on':
            self.logger.info(f"正在加载星座运势功能(首次运行可能会比较慢哦~)")
            from function import xingzuo
            xingzuo_key_list = list(xingzuo.character.xz_name_dict.keys())
            xingzuo_function = partial(xingzuo.func_xingzuo.xingZuo, func_send_text_msg=self.sendTextMsg)
            self.function_dict.update({key: xingzuo_function for key in xingzuo_key_list})
            # 每天晚上8点更新第二天的星座信息
            self.onEveryTime("20:00", xingzuo.func_xingzuo.getXzDataByWeb, time='tomorrow')
        self.logger.debug(f"功能点为：{self.function_dict}")
        if str(yuanshen).lower() == 'on':
            self.logger.info(f"正在加载原神功能")
            from function import yuanshen
            """原神扫码绑定"""
            self.function_dict["原神绑定"] = partial(
                yuanshen.generateLoginData,
                func_send_text_msg=self.sendTextMsg,
                func_send_img_msg=self.wcf.send_image)
            # 每10秒去查询一次米有社二维码登陆信息
            self.onEverySeconds(10, yuanshen.checkQrcode, func_send_text_msg=self.sendTextMsg)
            """原神米游社签到"""
            # self.function_dict["原神定时签到开启"] = partial(
            #     yuanshen.onSign, func_send_text_msg=self.sendTextMsg)
            # self.function_dict["原神定时签到关闭"] = partial(
            #     yuanshen.offSign, func_send_text_msg=self.sendTextMsg)
            self.function_dict["原神签到"] = partial(
                yuanshen.mhyBbsSign, func_send_text_msg=self.sendTextMsg
            )
            """米游币获取"""
            self.function_dict["米游币获取"] = partial(
                yuanshen.mhyBbsCoin, func_send_text_msg=self.sendTextMsg
            )

    def toAt(self, msg: WxMsg) -> bool:
        """处理被 @ 消息
        :param msg: 微信消息结构
        :return: 处理状态，`True` 成功，`False` 失败
        """
        return True

    def processMsg(self, msg: WxMsg) -> None:
        """当接收到消息的时候，会调用本方法。如果不实现本方法，则打印原始消息。
        此处可进行自定义发送的内容,如通过 msg.content 关键字自动获取当前天气信息，并发送到对应的群组@发送者
        群号：msg.roomid  微信ID：msg.sender  消息内容：msg.content
        content = "xx天气信息为："
        receivers = msg.roomid
        self.sendTextMsg(content, receivers, msg.sender)
        """

        # 群聊消息
        if msg.from_group():
            # 如果在群里被 @
            if msg.roomid not in self.groups:  # 不在配置的响应的群列表里，忽略
                return

            if str(msg.content).startswith(self.robot_name):  # 如果消息以配置文件自定义的机器人名称开头
                function_key = str(msg.content).split(self.robot_name)[-1]
                self.logger.debug(f"获取到的功能关键字为：{function_key}")
                if function_key in self.function_dict:
                    self.logger.debug(f"进入到了功能函数：{function_key}")
                    handler = self.function_dict.get(function_key)
                    handler(msg=msg)

                return

            if msg.is_at(self.wxid):  # 被@
                pass

            else:  # 其他消息
                pass

            return  # 处理完群聊信息，后面就不需要处理了

        # 非群聊信息，按消息类型进行处理
        if msg.type == 37:  # 好友请求
            # self.autoAcceptFriendRequest(msg)
            pass

        elif msg.type == 10000:  # 系统信息
            self.sayHiToNewFriend(msg)

        elif msg.type == 0x01:  # 文本消息
            # 让配置加载更灵活，自己可以更新配置。也可以利用定时任务更新。
            if msg.from_self():
                if msg.content == "^更新$":
                    self.config.reload()
                    self.logger.info("已更新")
            else:
                pass  # 闲聊

    def onMsg(self, msg: WxMsg) -> int:
        try:
            self.logger.info(msg)  # 打印信息
            self.processMsg(msg)
        except Exception as e:
            self.logger.error(e)

        return 0

    def enableRecvMsg(self) -> None:
        self.wcf.enable_recv_msg(self.onMsg)

    def sendTextMsg(self, msg: str, receiver: str, at_list: str = "") -> None:
        """ 发送消息
        :param msg: 消息字符串
        :param receiver: 接收人wxid或者群id
        :param at_list: 要@的wxid, @所有人的wxid为：nofity@all
        """
        # msg 中需要有 @ 名单中一样数量的 @
        ats = ""
        if at_list:
            wxids = at_list.split(",")
            for wxid in wxids:
                # 这里偷个懒，直接 @昵称。有必要的话可以通过 MicroMsg.db 里的 ChatRoom 表，解析群昵称
                ats += f" @{self.allContacts.get(wxid, '')}"

        # {msg}{ats} 表示要发送的消息内容后面紧跟@，例如 北京天气情况为：xxx @张三，微信规定需这样写，否则@不生效
        if ats == "":
            self.logger.info(f"To {receiver}: {msg}")
            self.wcf.send_text(f"{msg}", receiver, at_list)
        else:
            self.logger.info(f"To {receiver}: {ats}\r{msg}")
            self.wcf.send_text(f"{ats}\n{msg}", receiver, at_list)

    def getAllContacts(self) -> dict:
        """
        获取联系人（包括好友、公众号、服务号、群成员……）
        格式: {"wxid": "NickName"}
        """
        contacts = self.wcf.query_sql("MicroMsg.db", "SELECT UserName, NickName FROM Contact;")
        return {contact["UserName"]: contact["NickName"] for contact in contacts}

    def keepRunningAndBlockProcess(self) -> None:
        """
        保持机器人运行，不让进程退出
        """
        while True:
            self.runPendingJobs()
            time.sleep(1)

    def autoAcceptFriendRequest(self, msg: WxMsg) -> None:
        try:
            xml = ET.fromstring(msg.content)
            v3 = xml.attrib["encryptusername"]
            v4 = xml.attrib["ticket"]
            self.wcf.accept_new_friend(v3, v4)

        except Exception as e:
            self.logger.error(f"同意好友出错：{e}")

    def sayHiToNewFriend(self, msg: WxMsg) -> None:
        nickName = re.findall(r"你已添加了(.*)，现在可以开始聊天了。", msg.content)
        if nickName:
            # 添加了好友，更新好友列表
            self.allContacts[msg.sender] = nickName[0]
            self.sendTextMsg(f"Hi {nickName[0]}，我自动通过了你的好友请求。", msg.sender)
