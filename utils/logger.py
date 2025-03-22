import logging
import os
from utils.config_manager import ConfigManager

class Logger:
    @staticmethod
    def get_logger(name):
        config = ConfigManager().get_config()
        level = config.logging.level
        log_file = config.logging.file
        if level:
            pass
        else:
            level = logging.INFO

        # 创建日志记录器
        logger = logging.getLogger(name)
        logger.setLevel(level)

        # 创建控制台处理器并设置级别
        ch = logging.StreamHandler()
        ch.setLevel(level)

        # 创建格式化器并将其添加到处理器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
        ch.setFormatter(formatter)

        # 将处理器添加到记录器
        logger.addHandler(ch)

        # 可选：添加文件处理器
        if log_file:
            # 确保日志文件的目录存在
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            fh = logging.FileHandler(log_file)
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
        
        return logger
