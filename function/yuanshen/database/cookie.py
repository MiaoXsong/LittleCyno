from pydantic import BaseModel


class PrivateCookie(BaseModel):
    """
    米游社私人cookie
    """
    user_id: str
    """用户id"""
    uid: str
    """原神uid"""
    mys_id: str
    """米游社id"""
    cookie: str
    """cookie内容"""
    stoken: str
    """stoken内容"""
    status: int
    """cookie状态，0为疑似失效，1为可用，2为每日限制"""


class LastQuery(BaseModel):
    """
    上次查询的uid
    """
    user_id: str
    """用户id"""
    uid: str
    """原神uid"""
    last_time: str
    """上次查询的时间"""
