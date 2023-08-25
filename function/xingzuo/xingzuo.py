from datetime import datetime
from typing import Callable

from function.xingzuo.character import XinZuoProperty, xz_emoji_dict, xz_fanyi_dict
from logger.logger_object import xingzuo_logger
from database.async_sqlite import AsyncSQLite

db_name = 'XingZuo.db'
logger = xingzuo_logger
async_db = AsyncSQLite(db_name)


async def xing_zuo(send_txt_msg: Callable[[str, str, str], None], user_id: str, group_id: str, xz_name: str) -> str:
    date_now = datetime.now().strftime('%Y%m%d')
    query_sql = "SELECT * FROM xingzuo WHERE time = ? AND xz_name = ?"
    xz_tuple_list = await async_db.fetch(query_sql, (date_now, xz_name,))
    xz_data_dict = dict(zip(XinZuoProperty.__annotations__.keys(), xz_tuple_list[0]))
    logger.debug(f"查询到{date_now}的{xz_name}星座信息为{xz_data_dict}")

    summary_stars = '☆' * int(xz_data_dict['summary_star'])
    xinzuo_emoji = xz_emoji_dict[xz_name]
    xingzuo_str = f"{xinzuo_emoji}{xz_fanyi_dict[xz_name]}今日运势{summary_stars}{xinzuo_emoji}\n" \
                  f"【综合运势】{xz_data_dict['general_txt']}\n" \
                  f"【爱情运势】{xz_data_dict['love_txt']}\n" \
                  f"【事业运势】{xz_data_dict['work_txt']}\n" \
                  f"【财富运势】{xz_data_dict['money_txt']}\n" \
                  f"\n" \
                  f"{xinzuo_emoji}幸运颜色：{xz_data_dict['lucky_color']}\n" \
                  f"{xinzuo_emoji}幸运数字：{xz_data_dict['lucky_num']}\n" \
                  f"{xinzuo_emoji}贵人星座：{xz_data_dict['grxz']}\n" \
                  f"{xinzuo_emoji}今日提醒：{xz_data_dict['day_notice']}"
    logger.debug(f"回复的信息为\n{xingzuo_str}")
    send_txt_msg(xingzuo_str, group_id, user_id)

