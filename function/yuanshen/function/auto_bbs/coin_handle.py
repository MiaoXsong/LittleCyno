import asyncio
import random
import time
from typing import Tuple, Callable

from database.async_sqlite import AsyncSQLite
from function.yuanshen.utils.api import get_cookie, get_ds, get_old_version_ds, random_hex, random_text
from function.yuanshen.utils.requests import aiorequests
from function.yuanshen.database.mys import MihoyoBBSSub
from collections import defaultdict
from database import cache

from logger.logger_object import yuanshen_logger
from configuration import Config

logger = yuanshen_logger
robot_name = Config().ROBOT_NAME

db_name = 'YuanShen.db'
async_db = AsyncSQLite(db_name)

# 米游社的API列表
bbs_Cookieurl = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
bbs_Cookieurl2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'
bbs_Taskslist = 'https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState'
bbs_Signurl = 'https://bbs-api.mihoyo.com/apihub/app/api/signIn'
bbs_Listurl = 'https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1'
bbs_Detailurl = 'https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}'
bbs_Shareurl = 'https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1'
bbs_Likeurl = 'https://bbs-api.mihoyo.com/apihub/sapi/upvotePost'

mihoyo_bbs_List = [
    {
        'id': '1',
        'forumId': '1',
        'name': '崩坏3',
        'url': 'https://bbs.mihoyo.com/bh3/',
    },
    {
        'id': '2',
        'forumId': '26',
        'name': '原神',
        'url': 'https://bbs.mihoyo.com/ys/',
    },
    {
        'id': '3',
        'forumId': '30',
        'name': '崩坏2',
        'url': 'https://bbs.mihoyo.com/bh2/',
    },
    {
        'id': '4',
        'forumId': '37',
        'name': '未定事件簿',
        'url': 'https://bbs.mihoyo.com/wd/',
    },
    {
        'id': '5',
        'forumId': '34',
        'name': '大别野',
        'url': 'https://bbs.mihoyo.com/dby/',
    },
    {
        'id': '6',
        'forumId': '52',
        'name': '崩坏：星穹铁道',
        'url': 'https://bbs.mihoyo.com/sr/',
    },
    {
        'id': '8',
        'forumId': '57',
        'name': '绝区零',
        'url': 'https://bbs.mihoyo.com/zzz/'
    }
]


async def init_auto_coin() -> None:
    """
    创建米游币订阅表
    """
    create_auto_coin_table_query = """
            CREATE TABLE IF NOT EXISTS auto_coin (
                user_id TEXT PRIMARY KEY,
                group_id TEXT
            );
        """
    creat_query = create_auto_coin_table_query
    await async_db.execute(creat_query)


async def on_coin(user_id: str, group_id: str) -> str:
    cookie = await get_cookie(user_id, True, True)
    if not cookie:
        return f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~'
    elif cookie.stoken is None:
        return f'你绑定Cookie中没有login_ticket，请重新发送用【{robot_name}原神绑定】进行绑定~'
    insert_query = 'INSERT OR REPLACE INTO auto_coin(user_id, group_id) VALUES (?, ?)'
    await async_db.execute(insert_query, (user_id, group_id,))
    return f'你已成功(更新)订阅米游币获取功能~\n' \
           f'将在每天上午9点自动执行，执行结果将在执行完毕后统一发送！'


async def off_coin(user_id: str) -> str:
    cookie = await get_cookie(user_id, True, True)
    if not cookie:
        return f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~'
    elif cookie.stoken is None:
        return f'你绑定Cookie中没有login_ticket，请重新发送用【{robot_name}原神绑定】进行绑定~'
    select_query = 'SELECT user_id FROM auto_coin WHERE user_id = ?'
    if not await async_db.fetch(select_query, (user_id,)):
        return f'你还没有订阅米游币获取功能!\n' \
               f'请先发送【{robot_name}订阅米游币】进行订阅~'
    delete_query = 'DELETE FROM auto_coin WHERE user_id = ?'
    await async_db.execute(delete_query, (user_id,))
    return f'你已取消米游币获取功能订阅~\n' \
           f'如需使用，依旧可以发送【{robot_name}米游币】进行手动获取'


class MihoyoBBSCoin:
    """
    米游币获取
    """

    def __init__(self, cookies):
        self.headers: dict = {
            'DS': get_old_version_ds(),
            'cookie': cookies,
            'x-rpc-client_type': '2',
            'x-rpc-app_version': '2.34.1',
            'x-rpc-sys_version': '6.0.1',
            'x-rpc-channel': 'miyousheluodi',
            'x-rpc-device_id': random_hex(32),
            'x-rpc-device_name': random_text(random.randint(1, 10)),
            'x-rpc-device_model': 'Mi 10',
            'Referer': 'https://app.mihoyo.com',
            'Host': 'bbs-api.mihoyo.com',
            'User-Agent': 'okhttp/4.8.0'
        }
        self.postsList: list = []
        self.Task_do: dict = {
            'bbs_Sign': False,
            'bbs_Read_posts': False,
            'bbs_Read_posts_num': 3,
            'bbs_Like_posts': False,
            'bbs_Like_posts_num': 5,
            'bbs_Share': False
        }
        self.mihoyo_bbs_List: list = mihoyo_bbs_List
        self.available_coins: int = 0
        self.received_coins: int = 0
        self.total_coins: int = 0
        self.is_valid: bool = True
        self.state: str = ''

    async def run(self) -> Tuple[bool, str]:
        """
        执行米游币获取任务
        :return: 获取消息
        """
        await self.get_tasks_list()
        await self.get_list()
        tasks_list = [
            self.signing,
            self.read_posts,
            self.like_posts,
            self.share_post
        ]
        result = '米游币获取结果：'
        for task in tasks_list:
            if not self.is_valid:
                return False, self.state
            msg = await task()
            result += '\n' + msg
        return True, result

    async def get_tasks_list(self):
        """
        获取任务列表，用来判断做了哪些任务
        """
        data = await aiorequests.get(url=bbs_Taskslist, headers=self.headers)
        data = data.json()
        if data['retcode'] != 0:
            self.is_valid = False
            self.state = 'Cookie已失效' if data['retcode'] in [-100,
                                                               10001] else f"出错了:{data['message']} {data['message']}"
            logger.info(f'米游币自动获取 ➤➤ {self.state}')
            return self.state
        self.available_coins = data['data']['can_get_points']
        self.received_coins = data['data']['already_received_points']
        self.total_coins = data['data']['total_points']
        # 如果当日可获取米游币数量为0直接判断全部任务都完成了
        if self.available_coins == 0:
            self.Task_do['bbs_Sign'] = True
            self.Task_do['bbs_Read_posts'] = True
            self.Task_do['bbs_Like_posts'] = True
            self.Task_do['bbs_Share'] = True
        else:
            # 如果第0个大于或等于62则直接判定任务没做
            if data['data']['states'][0]['mission_id'] < 62:
                for i in data['data']['states']:
                    # 58是讨论区签到
                    if i['mission_id'] == 58:
                        if i['is_get_award']:
                            self.Task_do['bbs_Sign'] = True
                    # 59是看帖子
                    elif i['mission_id'] == 59:
                        if i['is_get_award']:
                            self.Task_do['bbs_Read_posts'] = True
                        else:
                            self.Task_do['bbs_Read_posts_num'] -= i[
                                'happened_times'
                            ]
                    # 60是给帖子点赞
                    elif i['mission_id'] == 60:
                        if i['is_get_award']:
                            self.Task_do['bbs_Like_posts'] = True
                        else:
                            self.Task_do['bbs_Like_posts_num'] -= i[
                                'happened_times'
                            ]
                    # 61是分享帖子
                    elif i['mission_id'] == 61:
                        if i['is_get_award']:
                            self.Task_do['bbs_Share'] = True
                            # 分享帖子，是最后一个任务，到这里了下面都是一次性任务，直接跳出循环
                            break
            logger.info(f'米游币自动获取 ➤➤ 该用户今天还可获取{self.available_coins}个米游币')

    async def get_list(self):
        """
        获取进行操作的帖子列表
        :return: 帖子id列表
        """
        req = await aiorequests.get(
            url=bbs_Listurl.format(random.choice([bbs['forumId'] for bbs in self.mihoyo_bbs_List])),
            headers=self.headers)
        data = req.json()
        self.postsList = [[d['post']['post_id'], d['post']['subject']] for d in data['data']['list'][:5]]
        logger.info('米游币自动获取 ➤➤ 获取帖子列表成功')

    # 进行签到操作
    async def signing(self):
        """
        讨论区签到
        """
        if self.Task_do['bbs_Sign']:
            return '讨论区签到：已经完成过了~'
        header = self.headers.copy()
        for i in self.mihoyo_bbs_List:
            header['DS'] = get_ds('', {'gids': i['id']}, True)
            req = await aiorequests.post(url=bbs_Signurl, json={'gids': i['id']}, headers=header)
            data = req.json()
            if data['retcode'] != 0:
                if data['retcode'] != 1034:
                    self.is_valid = False
                self.state = 'Cookie已失效' if data['retcode'] in [-100,
                                                                   10001] else f"出错了:{data['retcode']} {data['message']}" if \
                    data['retcode'] != 1034 else '遇验证码阻拦'
                logger.info(f'米游币自动获取 ➤➤ {self.state}')
                return f'讨论区签到：{self.state}'
            await asyncio.sleep(random.randint(15, 30))
        logger.info(f'米游币自动获取 ➤➤ 讨论区签到完成')
        return '讨论区签到：完成！'

    async def read_posts(self):
        """
        浏览帖子
        """
        if self.Task_do['bbs_Read_posts']:
            return '浏览帖子：已经完成过了~'
        num_ok = 0
        for i in range(self.Task_do['bbs_Read_posts_num']):
            req = await aiorequests.get(url=bbs_Detailurl.format(self.postsList[i][0]), headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            await asyncio.sleep(random.randint(5, 10))
        logger.info('米游币自动获取 ➤➤ 看帖任务完成')
        return f'浏览帖子：完成{str(num_ok)}个！'

    async def like_posts(self):
        """
        点赞帖子
        """
        if self.Task_do['bbs_Like_posts']:
            return '点赞帖子：已经完成过了~'
        num_ok = 0
        num_cancel = 0
        for i in range(self.Task_do['bbs_Like_posts_num']):
            req = await aiorequests.post(url=bbs_Likeurl,
                                         headers=self.headers,
                                         json={
                                             'post_id': self.postsList[i][0],
                                             'is_cancel': False,
                                         })
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            # 取消点赞
            await asyncio.sleep(random.randint(3, 6))
            req = await aiorequests.post(url=bbs_Likeurl,
                                         headers=self.headers,
                                         json={
                                             'post_id': self.postsList[i][0],
                                             'is_cancel': True,
                                         })
            data = req.json()
            if data['message'] == 'OK':
                num_cancel += 1
        logger.info('米游币自动获取 ➤➤ 点赞任务完成')
        await asyncio.sleep(random.randint(5, 10))
        return f'点赞帖子：完成{str(num_ok)}个{"，遇验证码" if num_ok == 0 else ""}！'

    async def share_post(self):
        """
        分享帖子
        """
        if self.Task_do['bbs_Share']:
            return '分享帖子：已经完成过了~'
        for _ in range(3):
            req = await aiorequests.get(
                url=bbs_Shareurl.format(self.postsList[0][0]),
                headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                return '分享帖子：完成！'
            else:
                await asyncio.sleep(random.randint(5, 10))
        logger.info('米游币自动获取 ➤➤ 分享任务完成')
        await asyncio.sleep(random.randint(5, 10))
        return '分享帖子：完成！'


async def mhy_bbs_coin(user_id: str) -> str:
    """
    执行米游币获取任务
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 结果
    """
    cookie = await get_cookie(user_id, True, True)
    if not cookie:
        return f'你还没有绑定原神账号！请发送【{robot_name}原神绑定】进行绑定~'
    elif cookie.stoken is None:
        return f'你绑定Cookie中没有login_ticket，请重新发送用【{robot_name}原神绑定】进行绑定~'
    uid = cookie.uid
    logger.info(f'米游币自动获取 ➤ 执行用户: {user_id}  UID: {uid}的米游币获取')
    get_coin_task = MihoyoBBSCoin(cookie.stoken)
    result, msg = await get_coin_task.run()
    return msg if result else f'UID:{uid}{msg}'


async def bbs_auto_coin(send_txt_msg: Callable[[str, str], None]):
    """
    指定时间，执行所有米游币获取订阅任务， 并将结果分群绘图发送
    """
    subs = []
    t = time.time()
    select_sql = """SELECT a.user_id, b.uid, a.group_id FROM auto_coin AS a
                    INNER JOIN private_cookies AS b ON a.user_id = b.user_id
    """
    auto_coin_tuple_list = await async_db.fetch(select_sql)
    attributes = ['user_id', 'uid', 'group_id']
    for auto_coin_tuple in auto_coin_tuple_list:
        auto_coin_dict = dict(zip(attributes, auto_coin_tuple))
        sub = MihoyoBBSSub(**auto_coin_dict)
        subs.append(sub)
    if not subs:
        logger.info(f'没有用户订阅米游币获取功能，跳过')
        return
    logger.info(f'米游币自动获取开始执行米游币自动获取，共{len(subs)}个任务，预计花费{round(100 * len(subs) / 60, 2)}分钟')
    coin_result_group = defaultdict(list)
    for sub in subs:
        if await cache.get(f'{sub.user_id}_get_myb'):    # 如果该用户正在手动执行中
            continue   # 直接跳过
        await cache.set(key=f'{sub.user_id}_get_myb', value='1', ttl=180)  # 设置一个三分钟的缓存，防止用户手动执行
        result = await mhy_bbs_coin(str(sub.user_id))
        coin_result_group[sub.group_id].append({
            'user_id': sub.user_id,
            'uid': sub.uid,
            'result': '出错' not in result and 'Cookie' not in result
        })
        await cache.delete(f'{sub.user_id}_get_myb')  # 执行后把缓存删掉
        await asyncio.sleep(random.randint(15, 25))

    for group_id, result_list in coin_result_group.items():
        result_num = len(result_list)
        if result_fail := len([result for result in result_list if not result['result']]):
            fails = '\n'.join(result['uid'] for result in result_list if not result['result'])
            msg = f'本群米游币自动获取共{result_num}个任务，其中成功{result_num - result_fail}个，失败{result_fail}个，失败的UID列表：\n{fails}'
        else:
            msg = f'本群米游币自动获取共{result_num}个任务，已全部完成'
        await asyncio.sleep(random.randint(3, 6))
        send_txt_msg(msg, group_id)
    logger.info(f'米游币自动获取完成，共花费{round((time.time() - t) / 60, 2)}分钟')
