#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil

import yaml


class Config(object):
    def __init__(self) -> None:
        self.reload()

    def _load_config(self) -> dict:
        pwd = os.path.dirname(os.path.abspath(__file__))
        try:
            with open(f"{pwd}/conf/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)
        except FileNotFoundError:
            shutil.copyfile(f"{pwd}/conf/config.yaml.template", f"{pwd}/conf/config.yaml")
            with open(f"{pwd}/conf/config.yaml", "rb") as fp:
                yconfig = yaml.safe_load(fp)

        return yconfig

    def reload(self) -> None:
        yconfig = self._load_config()
        """日志"""
        self.LOGGER_LEVEL = yconfig["logger"]["logger_level"]
        self.LOGGER_MAX_BYTES = yconfig["logger"]["logger_max_bytes"]
        self.LOGGER_BACKUP_COUNT = yconfig["logger"]["logger_backup_count"]
        """机器人"""
        self.ROBOT_NAME = yconfig["robot"]["robot_name"]
        self.GROUPS = yconfig["robot"]["groups"]["enable"]
        """功能"""
        self.CHOU_QIAN = yconfig["function"]["chouqian"]["switch"]
        self.XING_ZUO = yconfig["function"]["xingzuo"]["switch"]
        self.YUAN_SHEN = yconfig["function"]["yuanshen"]["switch"]
        self.EATDRINK = yconfig["function"]["eatdrink"]["switch"]
        """show_api"""
        self.SHOWAPI_ID = yconfig["showapi"]["appid"]
        self.SHOWAPI_SECRET = yconfig["showapi"]["appsecret"]
        """获取米游币开始时间"""
        self.MYBTIME = yconfig["miyoubi_start_time"]




