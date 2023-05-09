from datetime import datetime
import random
from mylogger import MyLogger
from wcferry import WxMsg
import asyncio
from database.async_sqlite import AsyncSQLite

logger = MyLogger(logger_name="chouqian").get_logger()
db_name = "ChouQian.db"
async_db = AsyncSQLite(db_name)


async def init_db() -> None:
    create_table_query = """
        CREATE TABLE IF NOT EXISTS qian_user (
            qian_user TEXT PRIMARY KEY,
            qian_num INTEGER,
            qian_date TEXT
        );
    """
    await async_db.execute(create_table_query)

    # async def jieqian(self, msg: WxMsg) -> None:
    #     """
    #     解签
    #     :param msg: 微信消息结构
    #     :return: 处理状态，`True` 成功，`False` 失败
    #     """
    #     not_cq_str = f"----------------\n" \
    #                  f"你今天还没抽签！\n" \
    #                  f"请先发送【{self.config.ROBOTNAME}抽签】噢~"
    #     qian_num = self.select_qianwen_num(msg.sender)
    #     if not qian_num:
    #         self.robot.sendTextMsg(not_cq_str, msg.roomid, msg.sender)
    #     else:
    #         jieqian_str = self.get_jieqian(qian_num)
    #         self.robot.sendTextMsg(jieqian_str, msg.roomid, msg.sender)

    # def get_jieqian(self, qianwen_num: int) -> str:
    #     conn = self.db.connect_to_db()
    #     jieqian_list, conn = self.db.select_to_db(sql_chouqian.select_jieqian_sql.format(qianwen_num), conn)
    #     conn.close()
    #     jieqian_str = f"----------------\n" \
    #                   f"🎐解释：{jieqian_list[0][0]}\n" \
    #                   f"----------------\n" \
    #                   f"🎐解签：{jieqian_list[0][1]}"
    #     return jieqian_str


async def chou_qian(msg: WxMsg) -> str:
    """
    抽签
    :param msg: 微信消息结构
    :return: None
    """

    async def select_qianwen_num(msg_sender: str) -> int or None:
        select_sql = " Select qian_num from qian_user Where qian_user = ?"
        qianwen_num_tuple = await async_db.fetch(select_sql, (msg_sender,))
        if not qianwen_num_tuple:
            return None
        else:
            return qianwen_num_tuple[0][0]

    async def update_qian_user_to_db(qian_user_tuple: tuple) -> None:
        insert_sql = "INSERT OR REPLACE INTO qian_user (qian_user, qian_num, qian_date) VALUES (?, ?, ?)"
        await async_db.execute(insert_sql, qian_user_tuple)

    async def get_qianwen(qianwen_num: int) -> str:
        select_sql = "Select qianwen from qian_zhuge Where id = ?"
        qianwen_tuple = await async_db.fetch(select_sql, (qianwen_num,))
        qianwen_str = f"🎐签诗：{qianwen_tuple[0][0]}"
        return qianwen_str

    yi_cq_str = f"----------------\n" \
                f"今天已经抽过啦！\n" \
                f"多抽不准噢！请明天再来试试吧~"
    qian_num = await select_qianwen_num(msg.sender)
    if not qian_num:
        qian_num = random.randint(1, 384)
        current_time = datetime.now().strftime("%H:%M:%S")
        qian_user_tuple = (msg.sender, qian_num, current_time)
        await update_qian_user_to_db(qian_user_tuple)
        qianwen_str = await get_qianwen(qian_num)
        cq_str = f"----------------\n" \
                 f"您抽到了第{qian_num}签~\n" \
                 f"----------------\n" \
                 f"{qianwen_str}\n" \
                 f"----------------\n" \
                 f"需要解签请回复【喵弟解签】"
    else:
        cq_str = yi_cq_str
    logger.info(cq_str)
    return cq_str


if __name__ == '__main__':
    # asyncio.run(init_db())
    asyncio.run(chou_qian())
