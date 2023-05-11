from function.xingzuo import func_xingzuo, character

"""初始化星座表"""
func_xingzuo.initXzTable()

"""获取当日星座数据"""
func_xingzuo.getXzDataByWeb('day')

"""获取明日星座数据"""
func_xingzuo.getXzDataByWeb('tomorrow')