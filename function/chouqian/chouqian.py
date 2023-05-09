from datetime import datetime
import random
from mylogger import MyLogger
from wcferry import WxMsg
from database.async_sqlite import AsyncSQLite
from configuration import Config

logger = MyLogger(logger_name="chouqian").get_logger()
config = Config()
robot_name = config.ROBOT_NAME
db_name = "ChouQian.db"
async_db = AsyncSQLite(db_name)


async def init_db() -> None:
    """
    创建签文用户表
    :return: None
    """
    create_table_query = """
        CREATE TABLE IF NOT EXISTS qian_user (
            qian_user TEXT PRIMARY KEY,
            qian_num INTEGER,
            qian_date TEXT
        );
    """
    await async_db.execute(create_table_query)


async def select_qianwen_num(msg_sender: str) -> int or None:
    """
    查询用户抽到的签文编号
    :param msg_sender: 微信号
    :return: 如果有数据返回 `int`签文号，否则返回`None`
    """
    select_sql = 'Select qian_num from qian_user Where qian_user = ?'
    qianwen_num_tuple = await async_db.fetch(select_sql, (msg_sender,))
    if not qianwen_num_tuple:
        return None
    else:
        return qianwen_num_tuple[0][0]


async def jieqian(msg: WxMsg) -> str:
    """
    解签
    :param msg: 微信消息结构
    :return: 处理状态，`True` 成功，`False` 失败
    """

    async def get_jieqian(qianwen_num: int) -> str:
        """
        根据签文号查询签文解释
        :param qianwen_num: 签文号
        :return: `str` 回复字符串
        """
        select_sql = 'Select jieshi, jieqian from qian_zhuge Where id = ?'
        jieqian_tuple = await async_db.fetch(select_sql, (qianwen_num,))
        jieqian_str = f"----------------\n" \
                      f"🎐解释：{jieqian_tuple[0][0]}\n" \
                      f"----------------\n" \
                      f"🎐解签：{jieqian_tuple[0][1]}"
        return jieqian_str

    not_cq_str = f"----------------\n" \
                 f"你今天还没抽签！\n" \
                 f"请先发送【{robot_name}抽签】噢~"
    qian_num = await select_qianwen_num(msg.sender)
    if not qian_num:
        jieqian_str = not_cq_str
    else:
        jieqian_str = await get_jieqian(qian_num)
    logger.debug(f"{jieqian_str}")
    return jieqian_str


async def chou_qian(msg: WxMsg) -> str:
    """
    抽签
    :param msg: 微信消息结构
    :return: `str` 回复字符串
    """

    async def update_qian_user_to_db(qian_user_tuple: tuple) -> None:
        """
        更新用户抽签信息
        :param qian_user_tuple: 用户抽签信息的元组
        :return: None
        """
        insert_sql = "INSERT OR REPLACE INTO qian_user (qian_user, qian_num, qian_date) VALUES (?, ?, ?)"
        await async_db.execute(insert_sql, qian_user_tuple)

    async def get_qianwen(qianwen_num: int) -> str:
        """
        根据签文编号查询签文信息
        :param qianwen_num: 签文号
        :return: `str` 签文信息
        """
        select_sql = 'Select qianwen from qian_zhuge Where id = ?'
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
                 f"需要解签请回复【{robot_name}解签】"
    else:
        cq_str = yi_cq_str
    logger.debug(cq_str)
    return cq_str
