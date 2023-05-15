# main code from lulu: https://github.com/lulu666lulu
import asyncio
import contextlib
import datetime
import json
import os
import random
import time
import uuid
import base64
from hashlib import md5
from io import BytesIO
from pathlib import Path
from string import ascii_letters
from string import digits
from typing import Callable

import qrcode
from PIL import Image

from function.yuanshen.utils.requests import aiorequests
from function.yuanshen.utils.api import get_bind_game_info
from logger.logger_object import yuanshen_logger
from database.async_sqlite import AsyncSQLite
from configuration import Config

robot_name = Config().ROBOT_NAME
CN_DS_SALT = 'JwYDpKvLj6MrMqqYU6jTKF17KNO2PXoS'

running_login_data = {}

db_name = 'YuanShen.db'
logger = yuanshen_logger
async_db = AsyncSQLite(db_name)

current_file_path = Path(__file__)
current_dir_path = current_file_path.parent.parent.parent
tmp_path = current_dir_path / "tmp"
if not os.path.exists(tmp_path):
    os.makedirs(tmp_path)


async def init_db() -> None:
    """
    创建原神Cookie表
    :return: None
    """
    create_private_cookies_table_query = """
        CREATE TABLE IF NOT EXISTS private_cookies (
            user_id TEXT PRIMARY KEY,
            uid INTEGER,
            mys_id INTEGER,
            cookie TEXT,
            stoken TEXT,
            status INTEGER default 1
        );
    """
    create_last_genshin_table_query = """
            CREATE TABLE IF NOT EXISTS last_genshin (
                user_id TEXT PRIMARY KEY,
                uid INTEGER,
                last_time TEXT
            );
        """
    sql_list = [create_private_cookies_table_query,
                create_last_genshin_table_query]
    tasks = [async_db.execute(sql) for sql in sql_list]
    await asyncio.gather(*tasks)


def md5_(self) -> str:
    return md5(self.encode()).hexdigest()


def get_ds(body=None, query=None) -> str:
    t = int(time.time())
    r = ''.join(random.choices(ascii_letters, k=6))
    b = json.dumps(body) if body else ''
    q = '&'.join((f"{k}={v}" for k, v in sorted(query.items()))) if query else ''
    h = md5_(f"salt={CN_DS_SALT}&t={t}&r={r}&b={b}&q={q}")
    return f"{t},{r},{h}"


async def get_stoken(aigis: str = '', data: dict = None):
    if data is None:
        data = {}
    resp = await aiorequests.post('https://passport-api.mihoyo.com/account/ma-cn-session/app/getTokenByGameToken',
                                  headers={'x-rpc-app_version': '2.41.0',
                                           'DS': get_ds(data),
                                           'x-rpc-aigis': aigis,
                                           'Content-Type': 'application/json',
                                           'Accept': 'application/json',
                                           'x-rpc-game_biz': 'bbs_cn',
                                           'x-rpc-sys_version': '11',
                                           'x-rpc-device_id': uuid.uuid4().hex,
                                           'x-rpc-device_fp': ''.join(
                                               random.choices((ascii_letters + digits), k=13)),
                                           'x-rpc-device_name': 'Chrome 108.0.0.0',
                                           'x-rpc-device_model': 'Windows 10 64-bit',
                                           'x-rpc-app_id': 'bll8iq97cem8',
                                           'x-rpc-client_type': '4',
                                           'User-Agent': 'okhttp/4.8.0'},
                                  json=data)
    return resp.json()


def generate_qrcode(url):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    bio = BytesIO()
    img.save(bio)
    # return f'base64://{base64.b64encode(bio.getvalue()).decode()}'
    return f'{base64.b64encode(bio.getvalue()).decode()}'


async def create_login_data():
    device_id = ''.join(random.choices((ascii_letters + digits), k=64))
    app_id = '4'
    data = {'app_id': app_id,
            'device': device_id}
    res = await aiorequests.post('https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/fetch?',
                                 json=data)
    url = res.json()['data']['url']
    ticket = url.split('ticket=')[1]
    return {'app_id': app_id,
            'ticket': ticket,
            'device': device_id,
            'url': url}


async def check_login(login_data: dict):
    data = {'app_id': login_data['app_id'],
            'ticket': login_data['ticket'],
            'device': login_data['device']}
    res = await aiorequests.post('https://hk4e-sdk.mihoyo.com/hk4e_cn/combo/panda/qrcode/query?',
                                 json=data)
    return res.json()


async def get_cookie_token(game_token: dict):
    res = await aiorequests.get(
        f"https://api-takumi.mihoyo.com/auth/api/getCookieAccountInfoByGameToken?game_token={game_token['token']}&account_id={game_token['uid']}")
    return res.json()


async def generate_login_data(send_text_msg: Callable[[str, str, str], None],
                              send_img_msg: Callable[[str, str], None], user_id: str, group_id: str):
    if str(user_id) in running_login_data:
        return '你已经在绑定中了，请扫描上一次的二维码'
    login_data = await create_login_data()
    running_login_data[str(user_id)] = login_data
    img_b64 = generate_qrcode(login_data['url'])
    running_login_data[str(user_id)]['img_b64'] = img_b64
    running_login_data[str(user_id)]['group_id'] = group_id
    send_msg = f'请在3分钟内使用【米游社】扫码并确认进行绑定(可以)~\n' \
               f'1.扫码即代表你同意将Cookie信息授权给【{robot_name}】\n' \
               f'2.扫码时会提示登录原神，实际不会上游戏，更不会把你游戏顶掉！\n' \
               f'3.其他人请不要乱扫，否则会将你的账号绑到TA身上！'
    timestamp = time.time()
    img_name = f'{user_id}_{timestamp}.png'
    img_tmp_path = tmp_path / img_name
    logger.debug(f'图片名称为：{img_name}')

    base64_data = base64.b64decode(img_b64)
    image_data = BytesIO(base64_data)
    img = Image.open(image_data)
    img.save(img_tmp_path)

    send_img_msg(str(img_tmp_path), group_id)
    send_text_msg(send_msg, group_id, user_id)
    os.remove(img_tmp_path)  # 发完后删掉


async def check_qrcode(send_txt_msg: Callable[[str, str, str], None]):
    with contextlib.suppress(RuntimeError):
        for user_id, data in running_login_data.items():
            send_msg = None
            status_data = await check_login(data)
            if status_data['retcode'] != 0:
                send_msg = '绑定二维码已过期，请重新发送扫码绑定指令'
                running_login_data.pop(user_id)
            elif status_data['data']['stat'] == 'Confirmed':
                game_token = json.loads(status_data['data']['payload']['raw'])
                running_login_data.pop(user_id)
                cookie_token_data = await get_cookie_token(game_token)
                stoken_data = await get_stoken(data={'account_id': int(game_token['uid']),
                                                     'game_token': game_token['token']})
                mys_id = stoken_data['data']['user_info']['aid']
                mid = stoken_data['data']['user_info']['mid']
                cookie_token = cookie_token_data['data']['cookie_token']
                stoken = stoken_data['data']['token']['token']
                if game_info := await get_bind_game_info(f"account_id={mys_id};cookie_token={cookie_token}", mys_id):
                    if not game_info['list']:
                        send_msg = '该账号尚未绑定任何游戏，请确认扫码的账号无误'
                    elif not (genshin_games := [{'uid': game['game_role_id'], 'nickname': game['nickname']} for game in
                                                game_info['list'] if game['game_id'] == 2]):
                        send_msg = '该账号尚未绑定原神，请确认扫码的账号无误'
                    else:
                        send_msg = '成功绑定原神账号：\n'
                        for info in genshin_games:
                            send_msg += f'{info["nickname"]}({info["uid"]}) '
                            ys_cookie = f"account_id={mys_id};cookie_token={cookie_token}"
                            ys_stoken = f'stuid={mys_id};stoken={stoken};mid={mid}'
                            private_cookie_tuple = (user_id, info['uid'], mys_id, ys_cookie, ys_stoken,)
                            insert_private_cookies_query = "INSERT OR REPLACE INTO private_cookies (" \
                                                           "user_id, uid, mys_id, cookie, stoken)" \
                                                           "VALUES (?, ?, ?, ?, ?)"
                            await async_db.execute(insert_private_cookies_query, private_cookie_tuple)
                        send_msg = send_msg.strip()
                        insert_cookie_last_genshin_query = "INSERT OR REPLACE INTO last_genshin (" \
                                                           "user_id, uid, last_time) VALUES (?, ?, ?)"
                        await async_db.execute(
                            insert_cookie_last_genshin_query,
                            (user_id, genshin_games[0]['uid'], datetime.datetime.now(),)
                        )

            if send_msg:
                send_txt_msg(send_msg, data['group_id'], user_id)
            if not running_login_data:
                break
            await asyncio.sleep(1)
