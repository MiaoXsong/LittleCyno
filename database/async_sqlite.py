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
