# -*- coding: utf-8 -*-
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from database.async_sqlite import AsyncSQLite
from mylogger import MyLogger


async def init_db() -> None:
    db_name = "ChouQian.db"
    async_db = AsyncSQLite(db_name)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS qian_zhuge (
        id INTEGER PRIMARY KEY,
        qianwen TEXT,
        jieshi TEXT,
        jieqian TEXT
    )
    """
    await async_db.execute(create_table_query)


class GetQianwenByWeb(object):
    def __init__(self) -> None:
        db_name = "ChouQian.db"
        self.url = 'https://www.ttlingqian.com/zhuge/'
        self.async_db = AsyncSQLite(db_name)
        self.my_logger = MyLogger(logger_name="chouqian")
        self.logger = self.my_logger.get_logger()

    async def get_qianwen_by_web(self) -> None:
        # 创建一个最大并发数为5的信号量
        sem = asyncio.Semaphore(5)

        async def fetch(session, url, i):
            async with sem:
                async with session.get(url) as response:
                    if response.status == 200:
                        html_content = await response.text()
                        soup = BeautifulSoup(html_content, "html.parser")
                        self.logger.info(f"正在提取第 {i} 签")

                        result_dict = {'num': i}
                        for item in soup.find_all('div', class_='qianresult_item'):
                            title = item.find('div', class_='qianresult_name').text.strip()
                            content = item.find('p').text.strip()
                            result_dict[title] = content

                        # 将结果存储到数据库
                        insert_query = "INSERT OR REPLACE INTO qian_zhuge (" \
                                       "id, qianwen, jieshi, jieqian) VALUES (?, ?, ?, ?)"
                        await self.async_db.execute(insert_query, tuple(result_dict.values()))
                    else:
                        self.logger.error(f"请求失败，状态码：{response.status}")

        async with aiohttp.ClientSession() as session:
            tasks = [fetch(session, f"{self.url}{str(i)}.html", i) for i in range(1, 385)]
            await asyncio.gather(*tasks)


async def get_qianwen_by_local() -> None:
    db_name = "ChouQian.db"
    async_db = AsyncSQLite(db_name)

    await init_db()

    with open("qian_zhuge.sql", 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 将SQL文件内容分割成单独的语句
    sql_statements = sql_content.split(';')

    # 创建一个最大并发数为5的信号量
    sem = asyncio.Semaphore(5)

    async def execute_statement(statement):
        async with sem:  # 将信号量放到函数内部
            await async_db.execute(statement)

    tasks = [execute_statement(statement) for statement in sql_statements]
    await asyncio.gather(*tasks)


async def get_qianwen_by_web_main() -> None:
    my_instance = GetQianwenByWeb()
    await init_db()
    await my_instance.get_qianwen_by_web()


if __name__ == "__main__":
    asyncio.run(get_qianwen_by_web_main())
