import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from configuration import Config

config = Config()
my_log_level = config.LOGGER_LEVEL
my_log_max_bytes = int(config.LOGGER_MAX_BYTES)
my_log_backup_count = int(config.LOGGER_BACKUP_COUNT)


class MyLogger:
    def __init__(self, logger_name="default", log_level=my_log_level, max_bytes=my_log_max_bytes,
                 backup_count=my_log_backup_count):
        current_file_path = Path(__file__)
        current_dir_path = current_file_path.parent
        self.log_dir = current_dir_path / "../logs"
        self.log_level = log_level
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.logger_name = logger_name
        self._configure_logger()

    def _configure_logger(self):
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)

        log_levels = {
            logging.DEBUG: "debug",
            logging.INFO: "info",
            logging.WARNING: "warning",
            logging.ERROR: "error",
            logging.CRITICAL: "critical"
        }

        for level, level_name in log_levels.items():
            file_handler = RotatingFileHandler(
                f"{self.log_dir}/cyno_{level_name}.log",
                encoding="utf-8",
                maxBytes=self.max_bytes,
                backupCount=self.backup_count
            )
            file_handler.setLevel(level)

            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)

        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


def main():
    my_logger = MyLogger(logger_name="test", log_level=logging.DEBUG)
    logger = my_logger.get_logger()

    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    logger.critical("这是一条严重消息")


if __name__ == "__main__":
    main()
