"""
工具模块
"""

from .platform import Platform
from .logger import Logger, get_logger

try:
    from .downloader import Downloader
    __all__ = [
        'Platform',
        'Logger',
        'get_logger',
        'Downloader'
    ]
except ImportError:
    # requests 未安装时跳过
    __all__ = [
        'Platform',
        'Logger',
        'get_logger',
    ]
