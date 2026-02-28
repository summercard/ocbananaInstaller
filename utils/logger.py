"""
日志工具
提供统一的日志记录接口
"""

import logging
import os
from datetime import datetime
from .platform import Platform

class Logger:
    """日志管理类"""

    def __init__(self, name="OpenClawInstaller", log_dir=None, level=logging.INFO):
        """
        初始化日志

        Args:
            name: 日志名称
            log_dir: 日志目录（默认为应用数据目录）
            level: 日志级别
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 设置日志目录
        if log_dir is None:
            log_dir = os.path.join(Platform.get_app_dir(), 'logs')

        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)

        # 设置日志文件路径
        log_file = os.path.join(
            log_dir,
            f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )

        # 创建文件处理器
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8'
        )
        file_handler.setLevel(level)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message):
        """调试信息"""
        self.logger.debug(message)

    def info(self, message):
        """一般信息"""
        self.logger.info(message)

    def warning(self, message):
        """警告信息"""
        self.logger.warning(message)

    def error(self, message):
        """错误信息"""
        self.logger.error(message)

    def critical(self, message):
        """严重错误"""
        self.logger.critical(message)

    def exception(self, message):
        """记录异常"""
        self.logger.exception(message)

    def get_logger(self):
        """获取原始logger对象"""
        return self.logger

# 全局日志实例
_logger = None

def get_logger():
    """获取全局日志实例"""
    global _logger
    if _logger is None:
        _logger = Logger()
    return _logger

def set_logger(logger):
    """设置全局日志实例"""
    global _logger
    _logger = logger

# 测试代码
if __name__ == '__main__':
    logger = Logger()
    logger.debug("这是调试信息")
    logger.info("这是一般信息")
    logger.warning("这是警告信息")
    logger.error("这是错误信息")

    try:
        1 / 0
    except:
        logger.exception("发生异常")
