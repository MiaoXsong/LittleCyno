#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
from threading import Thread
from typing import Callable

from wcferry import Wcf, WxMsg, wcf_pb2

from configuration import Config
from robot import Robot
from datetime import datetime
from logger.logger_object import main_logger

logger = main_logger


class MyWcf(Wcf):
    """重写Wcf类，处理消息时多线程异步"""

    def enable_recv_msg(self, callback: Callable[[WxMsg], None] = None) -> bool:
        """deprecated:: 3.7.0.30.13
        """

        def listening_msg():
            rsp = wcf_pb2.Response()
            self.msg_socket.dial(self.msg_url, block=True)
            while self._is_receiving_msg:
                try:
                    rsp.ParseFromString(self.msg_socket.recv_msg().bytes)
                except Exception as e:
                    pass
                else:
                    # callback(WxMsg(rsp.wxmsg))
                    # 为每个收到的消息启动一个新线程来处理
                    Thread(target=callback, args=(WxMsg(rsp.wxmsg),), daemon=True).start()
            # 退出前关闭通信通道
            self.msg_socket.close()

        if self._is_receiving_msg:
            return True

        if callback is None:
            return False

        req = wcf_pb2.Request()
        req.func = wcf_pb2.FUNC_ENABLE_RECV_TXT  # FUNC_ENABLE_RECV_TXT
        rsp = self._send_request(req)
        if rsp.status != 0:
            return False

        self._is_receiving_msg = True
        # 阻塞，把控制权交给用户
        # listening_msg()

        # 不阻塞，启动一个新的线程来接收消息
        Thread(target=listening_msg, name="GetMessage", daemon=True).start()

        return True


config = Config()
# wcf = Wcf(debug=True)
wcf = MyWcf(debug=True)


def handler(sig, frame):
    wcf.cleanup()  # 退出前清理环境
    exit(0)


signal.signal(signal.SIGINT, handler)

logger.info("正在启动机器人···")
robot = Robot(config, wcf)

# 机器人启动发送测试消息
# robot.sendTextMsg(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}：机器人启动成功！", "filehelper")
logger.info("机器人启动成功！")

# 接收消息
robot.enableRecvMsg()

# 让机器人一直跑
robot.keepRunningAndBlockProcess()
