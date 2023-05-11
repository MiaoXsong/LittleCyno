from logger.mylogger import MyLogger


main_logger = MyLogger(logger_name="main").get_logger()
robot_logger = MyLogger(logger_name="robot").get_logger()
chouqian_logger = MyLogger(logger_name="chouqian").get_logger()
xingzuo_logger = MyLogger(logger_name="xingzuo").get_logger()