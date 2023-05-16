from function.yuanshen.function.bind_cookie.func_get_cookie import initCookieTable, checkQrcode, generateLoginData
from function.yuanshen.function.auto_bbs.func_auto_bbs import initSignUserTable, onSign, offSign, mhyBbsSign, \
    mhyBbsCoin, bbsAutoCoin, initAutoCoin, onCoin, offCoin

"""初始化cookie相关表"""
initCookieTable()

"""初始化定时签到表"""
initSignUserTable()

"""初始化米游币获取表订阅"""
initAutoCoin()
