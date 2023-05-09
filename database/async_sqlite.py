import asyncio
from pathlib import Path

import aiosqlite


class AsyncSQLite:
    def __init__(self, db_name):
        # 创建一个Path对象
        current_file_path = Path(__file__)

        # 获取当前文件所在的目录
        current_dir_path = current_file_path.parent

        # 构建数据文件路径
        self.db_file = current_dir_path / db_name

    async def execute(self, query, *args):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.cursor()
            await cursor.execute(query, *args)
            await db.commit()

    async def fetch(self, query, *args):
        async with aiosqlite.connect(self.db_file) as db:
            cursor = await db.cursor()
            await cursor.execute(query, *args)
            result = await cursor.fetchall()
            return result


async def main():
    async_db = AsyncSQLite("test.db")

    # 创建表
    create_table_query = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    await async_db.execute(create_table_query)

    # 添加用户
    add_user_query = "INSERT INTO users (name, age) VALUES (?, ?)"
    await async_db.execute(add_user_query, ("Alice", 25))
    await async_db.execute(add_user_query, ("Bob", 30))

    # 获取用户
    get_users_query = "SELECT * FROM users"
    users = await async_db.fetch(get_users_query)

    for user in users:
        print(user)


if __name__ == '__main__':
    asyncio.run(main())
