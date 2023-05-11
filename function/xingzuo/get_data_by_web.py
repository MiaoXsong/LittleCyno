import asyncio
from datetime import datetime, timedelta

import aiohttp
from function.xingzuo import character
from database.async_sqlite import AsyncSQLite
from mylogger import MyLogger
from configuration import Config
from typing import Literal

db_name = 'XingZuo.db'
logger = MyLogger(logger_name="xingzuo").get_logger()
async_db = AsyncSQLite(db_name)


async def init_xz_table() -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS xingzuo (
        time TEXT,
        xz_name TEXT,
        summary_star TEXT,
        love_star TEXT,
        money_star TEXT,
        work_star TEXT,
        grxz TEXT,
        lucky_num TEXT,
        lucky_time TEXT,
        lucky_direction TEXT,
        day_notice TEXT,
        general_txt TEXT,
        love_txt TEXT,
        work_txt TEXT,
        money_txt TEXT,
        lucky_color TEXT,
        PRIMARY KEY (time, xz_name)
    )
    """
    logger.debug(f"正在创建星座表")
    await async_db.execute(create_table_query)


async def get_xz_data_by_web(time: Literal['day', 'tomorrow']) -> None:
    """
    从web获取星座数据并存入数据库
    :param time: `day`表示获取今天的数据，`tomorrow`表示获取明天的数据
    :return: None
    """

    async def existed_data(time: Literal['day', 'tomorrow']) -> list:
        if time == 'day':
            date = datetime.now().strftime('%Y%m%d')
        else:
            date = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')

        query_sql = "SELECT xz_name FROM xingzuo WHERE time = ?"
        xz_name_tuple_list = await async_db.fetch(query_sql, (date,))
        xz_name_set = {xz_name for xz_name_tuple in xz_name_tuple_list for xz_name in xz_name_tuple}
        logger.debug(f"{date}已存在{xz_name_set}星座的数据")

        xz_name_all_set = set(character.xz_name_list)
        need_xz_name_list = list(xz_name_all_set - xz_name_set)
        logger.debug(f"{date}需要获取{need_xz_name_list}星座的数据")

        return need_xz_name_list

    url = 'https://route.showapi.com/872-1'
    conf = Config()
    app_id = conf.SHOWAPI_ID
    app_secret = conf.SHOWAPI_SECRET

    # 创建一个最大并发数为5的信号量，我的API限制1秒一次，可以根据自己的API并发量调整
    sem = asyncio.Semaphore(1)

    async def fetch(session, url, xingzuo_name):
        data = {
            'showapi_appid': app_id,
            'showapi_sign': app_secret,
            'star': xingzuo_name,
            'needTomorrow': '1'
        }
        logger.debug(f"POST请求参数: {data}")
        async with sem:
            async with session.post(url, data=data) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type')
                    if 'application/json' in content_type:
                        xinzuo_data_json = await response.json()
                        time_xinzuo_data_json = xinzuo_data_json["showapi_res_body"][time]
                        time_xinzuo_data_json.update({"xz_name": xingzuo_name})
                        logger.debug(time_xinzuo_data_json)

                        # 解析 JSON 数据到 XinZuoProperty 对象
                        xinzuo_obj = character.XinZuoProperty(**time_xinzuo_data_json)
                        # 将 XinZuoProperty 对象的属性转换为可插入数据库的格式
                        xinzuo_data = tuple(xinzuo_obj.dict().values())
                        logger.debug(xinzuo_data)
                    else:
                        logger.error(f"Unexpected Content-Type: {content_type}")
                else:
                    logger.error(f"请求失败，状态码：{response.status}")
        await asyncio.sleep(1)
        insert_query = 'INSERT OR REPLACE INTO xingzuo VALUES' \
                       ' (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        await async_db.execute(insert_query, xinzuo_data)

    async with aiohttp.ClientSession() as session:
        # 为节省API的使用次数，只查询没有的数据就行了
        xz_name_list = await existed_data(time)
        tasks = [fetch(session, url, xz_name) for xz_name in xz_name_list]
        await asyncio.gather(*tasks)

# if __name__ == '__main__':
#     asyncio.run(get_xz_data_by_web("day"))
