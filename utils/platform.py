"""
平台检测工具
跨平台兼容性处理
"""

import platform
import os
import sys

class Platform:
    """平台检测类"""

    @staticmethod
    def get_system():
        """获取系统类型"""
        return platform.system()

    @staticmethod
    def is_windows():
        """是否为Windows"""
        return platform.system() == 'Windows'

    @staticmethod
    def is_macos():
        """是否为macOS"""
        return platform.system() == 'Darwin'

    @staticmethod
    def is_linux():
        """是否为Linux"""
        return platform.system() == 'Linux'

    @staticmethod
    def get_arch():
        """获取系统架构"""
        return platform.machine()

    @staticmethod
    def get_python_version():
        """获取Python版本"""
        return sys.version_info

    @staticmethod
    def check_python_version(min_version=(3, 10)):
        """检查Python版本是否满足要求"""
        current = sys.version_info
        return current >= min_version

    @staticmethod
    def get_home_dir():
        """获取用户主目录"""
        return os.path.expanduser('~')

    @staticmethod
    def get_app_dir():
        """获取应用数据目录"""
        if Platform.is_windows():
            return os.path.join(os.getenv('LOCALAPPDATA', '.'), 'OpenClawInstaller')
        elif Platform.is_macos():
            return os.path.join(Platform.get_home_dir(), 'Library', 'Application Support', 'OpenClawInstaller')
        else:
            return os.path.join(Platform.get_home_dir(), '.openclaw-installer')

    @staticmethod
    def get_path_separator():
        """获取路径分隔符"""
        return os.sep

    @staticmethod
    def get_newline():
        """获取换行符"""
        return os.linesep

# 测试代码
if __name__ == '__main__':
    print(f"系统: {Platform.get_system()}")
    print(f"是否为Windows: {Platform.is_windows()}")
    print(f"是否为macOS: {Platform.is_macos()}")
    print(f"是否为Linux: {Platform.is_linux()}")
    print(f"架构: {Platform.get_arch()}")
    print(f"Python版本: {Platform.get_python_version()}")
    print(f"Python版本满足要求(3.10+): {Platform.check_python_version()}")
    print(f"用户主目录: {Platform.get_home_dir()}")
    print(f"应用数据目录: {Platform.get_app_dir()}")
