import contextlib
import json
import hashlib
import random
import time
from typing import Literal, Optional, Union

from logger.logger_object import yuanshen_logger
from function.yuanshen.utils.requests import aiorequests
from function.yuanshen.database.cookie import PrivateCookie
from database.async_sqlite import AsyncSQLite
from configuration import Config

robot_name = Config().ROBOT_NAME
db_name = 'YuanShen.db'
logger = yuanshen_logger
async_db = AsyncSQLite(db_name)

GAME_RECORD_API = (
    'https://api-takumi-record.mihoyo.com/game_record/card/wapi/getGameRecordCard'
)
CHARACTER_SKILL_API = (
    'https://api-takumi.mihoyo.com/event/e20200928calculate/v1/sync/avatar/detail'
)
MONTH_INFO_API = 'https://hk4e-api.mihoyo.com/event/ys_ledger/monthInfo'
DAILY_NOTE_API = (
    'https://api-takumi-record.mihoyo.com/game_record/app/genshin/api/dailyNote'
)
SIGN_INFO_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/info'
SIGN_ACTION_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/sign'
SIGN_REWARD_API = 'https://api-takumi.mihoyo.com/event/bbs_sign_reward/home'


def md5(text: str) -> str:
    """
    md5加密

    :param text: 文本
    :return: md5加密后的文本
    """
    md5_ = hashlib.md5()
    md5_.update(text.encode())
    return md5_.hexdigest()


def random_hex(length: int) -> str:
    """
    生成指定长度的随机字符串

    :param length: 长度
    :return: 随机字符串
    """
    result = hex(random.randint(0, 16 ** length)).replace('0x', '').upper()
    if len(result) < length:
        result = '0' * (length - len(result)) + result
    return result


def get_old_version_ds(mhy_bbs: bool = False) -> str:
    """
    生成米游社旧版本headers的ds_token
    """
    if mhy_bbs:
        s = 'N50pqm7FSy2AkFz2B3TqtuZMJ5TOl3Ep'
    else:
        s = 'z8DRIUjNDT7IT5IZXvrUAxyupA1peND9'
    t = str(int(time.time()))
    r = ''.join(random.sample(string.ascii_lowercase + string.digits, 6))
    c = md5(f"salt={s}&t={t}&r={r}")
    return f"{t},{r},{c}"


def get_ds(q: str = '', b: dict = None, mhy_bbs_sign: bool = False) -> str:
    """
    生成米游社headers的ds_token

    :param q: 查询
    :param b: 请求体
    :param mhy_bbs_sign: 是否为米游社讨论区签到
    :return: ds_token
    """
    br = json.dumps(b) if b else ''
    if mhy_bbs_sign:
        s = 't0qEgfub6cvueAPgR5m9aQWWVciEer7v'
    else:
        s = 'xV8v4Qu54lUKrEYFZkJhB8cuOh9Asafs'
    t = str(int(time.time()))
    r = str(random.randint(100000, 200000))
    c = md5(f'salt={s}&t={t}&r={r}&b={br}&q={q}')
    return f'{t},{r},{c}'


def mihoyo_headers(cookie, q='', b=None) -> dict:
    """
    生成米游社headers
        :param cookie: cookie
        :param q: 查询
        :param b: 请求体
        :return: headers
    """
    return {
        'DS': get_ds(q, b),
        'Origin': 'https://webstatic.mihoyo.com',
        'Cookie': cookie,
        'x-rpc-app_version': "2.11.1",
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                      'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/',
    }


def mihoyo_sign_headers(cookie: str, extra_headers: Optional[dict] = None) -> dict:
    """
    生成米游社签到headers
        :param cookie: cookie
        :param extra_headers: 额外的headers参数
        :return: headers
    """
    header = {
        'User_Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        'Cookie': cookie,
        'x-rpc-device_id': random_hex(32),
        'Origin': 'https://webstatic.mihoyo.com',
        'X_Requested_With': 'com.mihoyo.hyperion',
        'DS': get_old_version_ds(mhy_bbs=True),
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id'
                   '=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
        'x-rpc-app_version': '2.35.2',
    }
    if extra_headers:
        header.update(extra_headers)
    return header


async def get_sign_reward_list() -> dict:
    headers = {
        'x-rpc-app_version': '2.11.1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 ('
                      'KHTML, like Gecko) miHoYoBBS/2.11.1',
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/',
    }
    resp = await aiorequests.get(
        url=SIGN_REWARD_API, headers=headers, params={'act_id': 'e202009291139501'}
    )
    data = resp.json()
    logger.debug(data)
    return data


async def check_retcode(data: dict, cookie_info, user_id: str, uid: str) -> bool:
    """
    检查数据响应状态冰进行响应处理
        :param data: 数据
        :param cookie_info: cookie信息
        :param user_id: 用户id
        :param uid: 原神uid
        :return: 数据是否有效
    """
    if not data:
        return False
    if data['retcode'] in [10001, -100]:
        if cookie_info.status == 1:
            cookie_info.status = 0
            update_query = "UPDATE private_cookies SET status = 0 WHERE user_id = ?"
            await async_db.execute(update_query, (cookie_info.user_id,))
            logger.info('原神Cookie', f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>疑似失效')
        elif cookie_info.status == 0:
            delete_query = "DELETE FROM private_cookies WHERE user_id = ?"
            await async_db.execute(delete_query, (cookie_info.user_id,))
            logger.info(
                '原神Cookie',
                f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>连续失效，<r>已删除</r>',
            )
        return False
    elif data['retcode'] == 10101:
        cookie_info.status = 2
        update_query = "UPDATE private_cookies SET status = 2 WHERE user_id = ?"
        await async_db.execute(update_query, (cookie_info.user_id,))
        logger.info(
            '原神Cookie', f'用户<m>{user_id}</m>的私人cookie<m>{uid}</m>已达到每日30次查询上限'
        )
        return False
    else:
        return True


async def get_bind_game_info(cookie: str, mys_id: str):
    """
    通过cookie，获取米游社绑定的原神游戏信息
    :param cookie: cookie
    :param mys_id: 米游社id
    :return: 原神信息
    """
    with contextlib.suppress(Exception):
        data = await aiorequests.get(
            url=GAME_RECORD_API,
            headers=mihoyo_headers(cookie, f'uid={mys_id}'),
            params={'uid': mys_id},
        )
        data = data.json()
        logger.debug(data)
        if data['retcode'] == 0:
            return data['data']
    return None


def mihoyo_sign_headers(cookie: str, extra_headers: Optional[dict] = None) -> dict:
    """
    生成米游社签到headers
        :param cookie: cookie
        :param extra_headers: 额外的headers参数
        :return: headers
    """
    header = {
        'User_Agent': 'Mozilla/5.0 (Linux; Android 12; Unspecified Device) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 miHoYoBBS/2.35.2',
        'Cookie': cookie,
        'x-rpc-device_id': random_hex(32),
        'Origin': 'https://webstatic.mihoyo.com',
        'X_Requested_With': 'com.mihoyo.hyperion',
        'DS': get_old_version_ds(mhy_bbs=True),
        'x-rpc-client_type': '5',
        'Referer': 'https://webstatic.mihoyo.com/bbs/event/signin-ys/index.html?bbs_auth_required=true&act_id'
                   '=e202009291139501&utm_source=bbs&utm_medium=mys&utm_campaign=icon',
        'x-rpc-app_version': '2.35.2',
    }
    if extra_headers:
        header.update(extra_headers)
    return header


async def get_cookie(
        user_id: str, check: bool = True, own: bool = False
) -> Union[None, PrivateCookie]:
    """
    获取可用的cookie
        :param user_id: 用户id
        :param uid: 原神uid
        :param check: 是否获取疑似失效的cookie
        :param own: 是否只获取和uid对应的cookie
    """
    if check:
        status_1 = 1
        status_2 = 1
    else:
        status_1 = 1
        status_2 = 0
    if own:
        select_query = "SELECT * FROM private_cookies WHERE user_id = ? AND (status = ? OR status = ?)"
        cookie_tuple_list = await async_db.fetch(select_query, (user_id, status_1, status_2,))
    else:
        select_query = "SELECT * FROM private_cookies WHERE status = ? OR status = ?"
        cookie_tuple_list = await async_db.fetch(select_query, (status_1, status_2,))
    logger.debug(f"cookie的信息为：{cookie_tuple_list}")
    if cookie_tuple_list:
        attributes = ['user_id', 'uid', 'mys_id', 'cookie', 'stoken', 'status']
        cookie_tuple = random.choice(cookie_tuple_list)  # 随机取一条Cookie
        cookie_dict = dict(zip(attributes, cookie_tuple))
        private_cookie = PrivateCookie(**cookie_dict)
        return private_cookie
    else:
        return None


async def get_mihoyo_private_data(
        user_id: Optional[str],
        mode: Literal['role_skill', 'month_info', 'daily_note', 'sign_info', 'sign_action'],
        role_id: Optional[str] = None,
        month: Optional[str] = None,
):
    cookie_info = await get_cookie(user_id, True, True)
    if not cookie_info:
        logger.debug(f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~')
        return f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~', None
    uid = cookie_info.uid
    server_id = 'cn_qd01' if uid[0] == '5' else 'cn_gf01'
    if mode == 'role_skill':
        data = await aiorequests.get(
            url=CHARACTER_SKILL_API,
            headers=mihoyo_headers(
                q=f'uid={uid}&region={server_id}&avatar_id={role_id}',
                cookie=cookie_info.cookie,
            ),
            params={"region": server_id, "uid": uid, "avatar_id": role_id},
        )
    elif mode == 'month_info':
        data = await aiorequests.get(
            url=MONTH_INFO_API,
            headers=mihoyo_headers(
                q=f'month={month}&bind_uid={uid}&bind_region={server_id}',
                cookie=cookie_info.cookie,
            ),
            params={"month": month, "bind_uid": uid, "bind_region": server_id},
        )
    elif mode == 'daily_note':
        data = await aiorequests.get(
            url=DAILY_NOTE_API,
            headers=mihoyo_headers(
                q=f'role_id={uid}&server={server_id}', cookie=cookie_info.cookie
            ),
            params={"server": server_id, "role_id": uid},
        )
    elif mode == 'sign_info':
        data = await aiorequests.get(
            url=SIGN_INFO_API,
            headers={
                'x-rpc-app_version': '2.11.1',
                'x-rpc-client_type': '5',
                'Origin': 'https://webstatic.mihoyo.com',
                'Referer': 'https://webstatic.mihoyo.com/',
                'Cookie': cookie_info.cookie,
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS '
                              'X) AppleWebKit/605.1.15 (KHTML, like Gecko) miHoYoBBS/2.11.1',
            },
            params={'act_id': 'e202009291139501', 'region': server_id, 'uid': uid},
        )
    elif mode == 'sign_action':
        data = await aiorequests.post(
            url=SIGN_ACTION_API,
            headers=mihoyo_sign_headers(cookie_info.cookie),
            json={'act_id': 'e202009291139501', 'uid': uid, 'region': server_id},
        )
    else:
        data = None
    data = data.json() if data else {'retcode': 999}
    logger.debug(data)
    if await check_retcode(data, cookie_info, user_id, uid):
        return data, cookie_info.uid
    else:
        return f'你的UID{uid}的cookie疑似失效了', None
