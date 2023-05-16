from pydantic.main import BaseModel


class MihoyoBBSSub(BaseModel):
    """
    米游社米游币获取订阅
    """
    user_id: str
    """用户id"""
    uid: int
    """原神uid"""
    group_id: str
    """订阅所在的群号"""
