import asyncio
import datetime
from typing import Callable, Tuple

from database.async_sqlite import AsyncSQLite
from logger.logger_object import yuanshen_logger
from function.yuanshen.function.auto_bbs.draw import SignResult, draw_result

db_name = 'YuanShen.db'
logger = yuanshen_logger
async_db = AsyncSQLite(db_name)


async def init_db() -> None:
    """
    创建原神签到表
    """
    create_on_sign_table_query = """
            CREATE TABLE IF NOT EXISTS on_sign (
                user_id TEXT PRIMARY KEY,
                group_id TEXT
            );
        """
    sql_list = [create_on_sign_table_query]
    tasks = [async_db.execute(sql) for sql in sql_list]
    await asyncio.gather(*tasks)


async def is_get_cookie(user_id: str) -> tuple:
    """
    检查用户是否已经有米有社Cookie
    """
    null_tuple = ()
    select_query = 'SELECT mys_id FROM private_cookies WHERE user_id = ?'
    user_id_tuple_list = await async_db.fetch(select_query, (user_id,))
    if user_id_tuple_list:
        return user_id_tuple_list[0]
    else:
        return null_tuple


async def on_sign(send_txt_msg: Callable[[str, str, str], None],
                  user_id: str, group_id: str, robot_name: str) -> None:
    """
    开启米有社定时签到
    """
    select_query = 'SELECT user_id FROM on_sign WHERE user_id = ?'
    user_id_tuple = await async_db.fetch(select_query, (user_id,))
    mys_id_tuple = await is_get_cookie(user_id=user_id)
    if not user_id_tuple:
        if mys_id_tuple:
            insert_query = "INSERT OR REPLACE INTO on_sign(user_id, group_id) VALUES (?, ?)"
            await async_db.execute(insert_query, (user_id, group_id,))
            send_msg = f'米有社ID: {mys_id_tuple[0]}\n' \
                       f'【原神定时签到】开启成功'
        else:
            send_msg = f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~'
    else:
        send_msg = f'米有社ID: {mys_id_tuple[0]}\n' \
                   f'已经开启了米有社【原神定时签到】，请勿重复开启\n' \
                   f'如需更换群，请先发送【{robot_name}原神定时签到关闭】再重新开启'
    send_txt_msg(send_msg, group_id, user_id)


async def off_sign(send_txt_msg: Callable[[str, str, str], None],
                   user_id: str, group_id: str, robot_name: str) -> None:
    """
    关闭米有社定时签到
    """
    mys_id_tuple = await is_get_cookie(user_id=user_id)
    if mys_id_tuple:
        select_query = 'SELECT user_id FROM on_sign WHERE user_id = ?'
        user_id_tuple_list = await async_db.fetch(select_query, (user_id,))
        if user_id_tuple_list:
            delete_query = "DELETE FROM on_sign WHERE user_id = ?"
            await async_db.execute(delete_query, (user_id,))
            send_msg = f'米有社ID: {mys_id_tuple[0]}\n' \
                       f'【原神定时签到】已关闭'
        else:
            send_msg = f'米有社ID: {mys_id_tuple[0]}\n' \
                       f'没有开启【原神定时签到】！'
    else:
        send_msg = f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~'
    send_txt_msg(send_msg, group_id, user_id)


async def mhy_bbs_sign(user_id: str, uid: str) -> Tuple[SignResult, str]:
    """
    执行米游社原神签到，返回签到成功天数或失败原因
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 签到成功天数或失败原因
    """
    insert_cookie_last_genshin_query = "INSERT OR REPLACE INTO last_genshin (" \
                                       "user_id, uid, last_time) VALUES (?, ?, ?)"
    await async_db.execute(
        insert_cookie_last_genshin_query,
        (user_id, uid, datetime.datetime.now(),)
    )
    sign_info = await get_mihoyo_private_data(uid, user_id, 'sign_info')
    if isinstance(sign_info, str):
        logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '未绑定私人cookie或已失效', False)
        await MihoyoBBSSub.filter(user_id=user_id, uid=uid).delete()
        return SignResult.FAIL, sign_info
    elif sign_info['data']['is_sign']:
        signed_days = sign_info['data']['total_sign_day'] - 1
        logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '今天已经签过了', True)
        if sign_reward_list:
            return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
        else:
            return SignResult.DONE, f'UID{uid}今天已经签过了'
    for i in range(3):
        sign_data = await sign_action(user_id, uid)
        if isinstance(sign_data, str):
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, f'获取数据失败, {sign_data}', False)
            return SignResult.FAIL, f'{uid}签到失败，{sign_data}\n'
        elif sign_data['retcode'] == -5003:
            signed_days = sign_info['data']['total_sign_day'] - 1
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '今天已经签过了', True)
            if sign_reward_list:
                return SignResult.DONE, f'UID{uid}今天已经签过了，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
            else:
                return SignResult.DONE, f'UID{uid}今天已经签过了'
        elif sign_data['retcode'] != 0:
            logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid},
                        f'获取数据失败，code为{sign_data["retcode"]}， msg为{sign_data["message"]}', False)
            return SignResult.FAIL, f'{uid}获取数据失败，签到失败，msg为{sign_data["message"]}\n'
        else:
            if sign_data['data']['success'] == 0:
                logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '签到成功', True)
                signed_days = sign_info['data']['total_sign_day']
                if sign_reward_list:
                    return SignResult.SUCCESS, f'签到成功，获得的奖励为\n{sign_reward_list[signed_days]["name"]}*{sign_reward_list[signed_days]["cnt"]}'
                else:
                    return SignResult.SUCCESS, '签到成功'
            else:
                wait_time = random.randint(90, 120)
                logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, f'出现验证码，等待{wait_time}秒后进行第{i + 1}次尝试绕过', False)
                await asyncio.sleep(wait_time)
    logger.info('米游社原神签到', '➤', {'用户': user_id, 'UID': uid}, '尝试3次签到失败，无法绕过验证码', False)
    return SignResult.FAIL, f'{uid}签到失败，无法绕过验证码'
