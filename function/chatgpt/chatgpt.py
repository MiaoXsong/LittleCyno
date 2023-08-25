#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime

import openai

from configuration import Config
from logger.logger_object import chatgpt_logger
logger = chatgpt_logger

key = Config().CHATGPT_KEY
api = Config().CHATGPT_API
proxy = Config().CHATGPT_PROXY
contexts = Config().CHATGPT_CONTEXTS

conversation_list = {}


async def get_answer(question: str, wxid: str) -> [str, bool]:
    openai.api_key = key
    # 自己搭建或第三方代理的接口
    openai.api_base = api
    if proxy:
        openai.proxy = {"http": proxy, "https": proxy}

    # wxid或者roomid,个人时为微信id，群消息时为群id
    await updateMessage(wxid, question, "user")

    try:
        ret = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_list[wxid],
            temperature=0.2
        )

        rsp = ret["choices"][0]["message"]["content"]
        rsp = rsp[2:] if rsp.startswith("\n\n") else rsp
        rsp = rsp.replace("\n\n", "\n")
        await updateMessage(wxid, rsp, "assistant")
        result = True
    except openai.error.AuthenticationError as e3:
        rsp = "OpenAI API 认证失败！"
        logger.error(f"OpenAI API 认证失败，请检查 API 密钥是否正确")
        result = False
    except openai.error.APIConnectionError as e2:
        rsp = "无法连接到 OpenAI API，请重试！"
        logger.error(f"无法连接到 OpenAI API，请检查网络连接")
        result = False
    except openai.error.APIError as e1:
        rsp = "OpenAI API 发生了错误，请重试！："
        logger.error(f"OpenAI API 返回了错误：{str(e1)}")
        result = False
    except Exception as e0:
        rsp = "发生未知错误，请重试！"
        logger.error(f"发生未知错误：{str(e0)}")
        result = False

    # print(conversation_list[wxid])

    return rsp, result


async def get_contextual_content(wxid: str) -> str:
    q_count = 1
    if wxid in conversation_list.keys():
        answer = '你目前的上下文内容如下：\n'
        for cont in conversation_list[wxid]:
            if cont["role"] == "user":
                answer = answer + f"问题{q_count}: {cont['content']}\n"
                q_count = q_count + 1
        answer = answer.rstrip("\n")
    else:
        answer = '你还没有问过我问题呢，来试着问问吧~'
    return answer


async def del_contextual_content(wxid: str) -> str:
    if wxid in conversation_list.keys():
        del conversation_list[wxid]
        answer = '已成功删除上下文记录~'
    else:
        answer = '你还没有问过我问题呢，来试着问问吧~'
    return answer


async def updateMessage(wxid: str, question: str, role: str) -> None:
    # 初始化聊天记录,组装系统信息
    if wxid not in conversation_list.keys():
        question_ = []
        conversation_list[wxid] = question_

    # 当前问题
    content_question_ = {"role": role, "content": question}
    conversation_list[wxid].append(content_question_)

    for cont in conversation_list[wxid]:
        if cont["role"] != "system":
            continue

    # 只存储 contexts 条记录(配置文件中改数量)，超过滚动清除
    i = len(conversation_list[wxid])
    if i > contexts:
        logger.debug('删除多余的记录')
        # 删除多余的记录，倒着删
        del conversation_list[wxid][0]


if __name__ == "__main__":
    while True:
        q = input(">>> ")
        try:
            time_start = datetime.now()  # 记录开始时间
            print(asyncio.run(get_answer(q, "wxid")))
            time_end = datetime.now()  # 记录结束时间
            print(f"{round((time_end - time_start).total_seconds(), 2)}s")  # 计算的时间差为程序的执行时间，单位为秒/s
        except Exception as e:
            print(e)
