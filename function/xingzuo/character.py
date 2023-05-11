from pydantic.main import BaseModel


class XinZuoProperty(BaseModel):
    """
    星座属性类
    """
    time: str
    """时间"""
    xz_name: str
    """星座名称"""
    summary_star: str
    """综合指数，最高5分"""
    love_star: str
    """爱情指数，最高5分"""
    money_star: str
    """财富指数，最高5分"""
    work_star: str
    """工作指数，最高5分"""
    grxz: str
    """贵人星座"""
    lucky_num: str
    """幸运数字"""
    lucky_time: str
    """吉时"""
    lucky_direction: str
    """吉利方位"""
    day_notice: str
    """今日提醒"""
    general_txt: str
    """运势简评"""
    love_txt: str
    """爱情运势"""
    work_txt: str
    """工作运势"""
    money_txt: str
    """财富运势"""
    lucky_color: str
    """吉色"""


xz_name_dict = {
    '白羊': 'baiyang',
    '金牛': 'jinniu',
    '双子': 'shuangzi',
    '巨蟹': 'juxie',
    '狮子': 'shizi',
    '处女': 'chunv',
    '天秤': 'tiancheng',
    '天蝎': 'tianxie',
    '射手': 'sheshou',
    '摩羯': 'mojie',
    '水瓶': 'shuiping',
    '双鱼': 'shuangyu'
}

xz_pinyin_list = [
    'baiyang',
    'jinniu',
    'shuangzi',
    'juxie',
    'shizi',
    'chunv',
    'tiancheng',
    'tianxie',
    'sheshou',
    'mojie',
    'shuiping',
    'shuangyu'
]

xz_emoji_dict = {
    'baiyang': '♈',
    'jinniu': '♉',
    'shuangzi': '♊',
    'juxie': '♋',
    'shizi': '♌',
    'chunv': '♍',
    'tiancheng': '♎',
    'tianxie': '♏',
    'sheshou': '♐',
    'mojie': '♑',
    'shuiping': '♒',
    'shuangyu': '♓'
}

xz_fanyi_dict = {
    'baiyang': '白羊座',
    'jinniu': '金牛座',
    'shuangzi': '双子座',
    'juxie': '巨蟹座',
    'shizi': '狮子座',
    'chunv': '处女座',
    'tiancheng': '天秤座',
    'tianxie': '天蝎座',
    'sheshou': '射手座',
    'mojie': '摩羯座',
    'shuiping': '水瓶座',
    'shuangyu': '双鱼座'
}