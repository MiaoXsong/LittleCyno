



def sget_today_xingzuo_data(self, xinzuo_name: str) -> str or None:
    data_dict = self.today_xingzuo_data(xinzuo_name)
    if not data_dict:
        return None
    today = datetime.now().date()
    given_date = datetime.strptime(data_dict['time'], '%Y%m%d').date()
    no_data_str = f"今天的星座运势还没更新呢，请稍后再试试吧~"
    if today != given_date:
        return no_data_str
    xinzuo_emoji_dict = {
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
    xinzuo_fanyi_dict = {
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
    summary_stars = '☆' * data_dict['summary_star']
    xinzuo_emoji = xinzuo_emoji_dict[xinzuo_name]
    today_xingzuo_str = f"{xinzuo_emoji}{xinzuo_fanyi_dict[xinzuo_name]}今日运势{summary_stars}{xinzuo_emoji}\n" \
                        f"【综合运势】{data_dict['general_txt']}\n" \
                        f"【爱情运势】{data_dict['love_txt']}\n" \
                        f"【事业运势】{data_dict['work_txt']}\n" \
                        f"【财富运势】{data_dict['money_txt']}\n" \
                        f"\n" \
                        f"{xinzuo_emoji}幸运颜色：{data_dict['lucky_color']}\n" \
                        f"{xinzuo_emoji}幸运数字：{data_dict['lucky_num']}\n" \
                        f"{xinzuo_emoji}贵人星座：{data_dict['grxz']}\n" \
                        f"{xinzuo_emoji}今日提醒：{data_dict['day_notice']}"

    return today_xingzuo_str