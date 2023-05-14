import asyncio
from typing import Callable

from database.async_sqlite import AsyncSQLite
from logger.logger_object import yuanshen_logger

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
