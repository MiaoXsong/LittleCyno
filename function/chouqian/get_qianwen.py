# -*- coding: utf-8 -*-
import asyncio
from pathlib import Path

import aiohttp
from bs4 import BeautifulSoup
from database.async_sqlite import AsyncSQLite
from mylogger import MyLogger


logger = MyLogger(logger_name="chouqian").get_logger()
db_name = "ChouQian.db"
async_db = AsyncSQLite(db_name)
url = 'https://www.ttlingqian.com/zhuge/'


async def init_db() -> None:
    """
    初始化数据表
    :return:
    """
    create_table_query = """
    CREATE TABLE IF NOT EXISTS qian_zhuge (
        id INTEGER PRIMARY KEY,
        qianwen TEXT,
        jieshi TEXT,
        jieqian TEXT
    )
    """
    logger.debug(f"正在创建签文表")
    await async_db.execute(create_table_query)


async def get_qianwen_by_web() -> None:
    await init_db()
    # 创建一个最大并发数为5的信号量
    sem = asyncio.Semaphore(5)

    async def fetch(session, url, i):
        async with sem:
            async with session.get(url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, "html.parser")
                    logger.debug(f"正在提取第 {i} 签")

                    result_dict = {'num': i}
                    for item in soup.find_all('div', class_='qianresult_item'):
                        title = item.find('div', class_='qianresult_name').text.strip()
                        content = item.find('p').text.strip()
                        result_dict[title] = content

                    # 将结果存储到数据库
                    insert_query = "INSERT OR REPLACE INTO qian_zhuge (" \
                                   "id, qianwen, jieshi, jieqian) VALUES (?, ?, ?, ?)"
                    logger.debug(f"正在插入第 {i} 签")
                    await async_db.execute(insert_query, tuple(result_dict.values()))
                else:
                    logger.error(f"请求失败，状态码：{response.status}")

    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, f"{url}{str(i)}.html", i) for i in range(1, 385)]
        await asyncio.gather(*tasks)


async def get_qianwen_by_local() -> None:
    sql_file_name = 'qian_zhuge.sql'
    # 创建一个Path对象
    current_file_path = Path(__file__)

    # 获取当前文件所在的目录
    current_dir_path = current_file_path.parent

    # 构建数据文件路径
    sql_file = current_dir_path / sql_file_name

    await init_db()

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 将SQL文件内容分割成单独的语句
    sql_statements = sql_content.split(';')

    # 防止数据库锁死。。创建一个最大并发数为3的信号量
    sem = asyncio.Semaphore(3)

    async def execute_statement(statement):
        async with sem:  # 将信号量放到函数内部
            logger.debug(f"{statement}")
            await async_db.execute(statement)

    tasks = [execute_statement(statement) for statement in sql_statements]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(get_qianwen_by_web())
    asyncio.run(get_qianwen_by_local())

