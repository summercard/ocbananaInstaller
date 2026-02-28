"""
环境检查工具
检查系统环境是否满足OpenClaw安装要求
"""

import subprocess
import shutil
import sys
import os
from typing import Dict, Tuple, List
from utils.logger import get_logger
from utils.platform import Platform

class EnvChecker:
    """环境检查类"""

    def __init__(self):
        self.logger = get_logger()
        self.results = {}

    def check_all(self) -> Dict[str, bool]:
        """
        执行所有环境检查

        Returns:
            检查结果字典 {检查项: 是否通过}
        """
        self.logger.info("开始环境检查...")

        self.results = {
            'python_version': self.check_python_version(),
            'nodejs_version': self.check_nodejs_version(),
            'disk_space': self.check_disk_space(),
            'network': self.check_network()
        }

        # 打印检查结果
        self._print_results()

        return self.results

    def check_python_version(self, min_version=(3, 10)) -> bool:
        """
        检查Python版本

        Args:
            min_version: 最低版本要求（元组）

        Returns:
            满足要求返回True，否则返回False
        """
        try:
            current = sys.version_info
            is_valid = current >= min_version

            version_str = f"{current.major}.{current.minor}.{current.micro}"
            min_version_str = f"{min_version[0]}.{min_version[1]}"

            if is_valid:
                self.logger.info(f"✓ Python版本检查通过: {version_str} >= {min_version_str}")
            else:
                self.logger.error(f"✗ Python版本不足: {version_str} < {min_version_str}")

            return is_valid

        except Exception as e:
            self.logger.error(f"✗ Python版本检查失败: {e}")
            return False

    def check_nodejs_version(self, min_version=(14, 0, 0)) -> bool:
        """
        检查Node.js版本

        Args:
            min_version: 最低版本要求（元组）

        Returns:
            满足要求返回True，否则返回False
        """
        try:
            # 检查node命令是否存在
            if not shutil.which('node'):
                self.logger.warning("✗ Node.js未安装")
                self.logger.info("  请访问 https://nodejs.org/ 下载安装")
                return False

            # 获取Node.js版本
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error(f"✗ 获取Node.js版本失败: {result.stderr}")
                return False

            # 解析版本号（格式: v18.17.0）
            version_str = result.stdout.strip()
            if not version_str.startswith('v'):
                self.logger.error(f"✗ Node.js版本格式异常: {version_str}")
                return False

            version_str = version_str[1:]  # 去掉'v'前缀
            version_parts = version_str.split('.')
            version = tuple(int(part) for part in version_parts[:3])

            is_valid = version >= min_version
            min_version_str = f"{min_version[0]}.{min_version[1]}.{min_version[2]}"

            if is_valid:
                self.logger.info(f"✓ Node.js版本检查通过: {version_str} >= {min_version_str}")
            else:
                self.logger.warning(f"✗ Node.js版本不足: {version_str} < {min_version_str}")
                self.logger.info("  请升级Node.js: https://nodejs.org/")

            return is_valid

        except subprocess.TimeoutExpired:
            self.logger.error("✗ Node.js版本检查超时")
            return False
        except Exception as e:
            self.logger.error(f"✗ Node.js版本检查失败: {e}")
            return False

    def check_disk_space(self, min_space_mb=500) -> bool:
        """
        检查磁盘可用空间

        Args:
            min_space_mb: 最低空间要求（MB）

        Returns:
            满足要求返回True，否则返回False
        """
        try:
            # 获取当前工作目录的磁盘信息
            usage = shutil.disk_usage(os.getcwd())

            # 转换为MB
            free_mb = usage.free / (1024 * 1024)

            if free_mb >= min_space_mb:
                free_mb_str = f"{free_mb:.0f}MB"
                self.logger.info(f"✓ 磁盘空间检查通过: {free_mb_str} >= {min_space_mb}MB")
                return True
            else:
                free_mb_str = f"{free_mb:.0f}MB"
                self.logger.warning(f"✗ 磁盘空间不足: {free_mb_str} < {min_space_mb}MB")
                return False

        except Exception as e:
            self.logger.error(f"✗ 磁盘空间检查失败: {e}")
            return False

    def check_network(self, timeout=5) -> bool:
        """
        检查网络连接

        Args:
            timeout: 超时时间（秒）

        Returns:
            网络可用返回True，否则返回False
        """
        try:
            # 测试连接到GitHub（OpenClaw的托管平台）
            import socket

            host = 'github.com'
            port = 443

            self.logger.debug(f"测试网络连接: {host}:{port}")

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)

            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                self.logger.info(f"✓ 网络连接检查通过: 可连接到 {host}")
                return True
            else:
                self.logger.warning(f"✗ 网络连接检查失败: 无法连接到 {host}")
                return False

        except socket.timeout:
            self.logger.warning("✗ 网络连接检查超时")
            return False
        except Exception as e:
            self.logger.error(f"✗ 网络连接检查失败: {e}")
            return False

    def _print_results(self):
        """打印检查结果摘要"""
        self.logger.info("=" * 50)
        self.logger.info("环境检查结果摘要:")

        total = len(self.results)
        passed = sum(1 for v in self.results.values() if v)

        for name, status in self.results.items():
            status_str = "✓ 通过" if status else "✗ 失败"
            self.logger.info(f"  {name}: {status_str}")

        self.logger.info("=" * 50)
        self.logger.info(f"总计: {passed}/{total} 通过")

    def get_requirements(self) -> List[str]:
        """
        获取未满足的环境要求

        Returns:
            未满足要求的列表
        """
        requirements = []

        if not self.results.get('python_version', True):
            requirements.append("Python 3.10 或更高版本")

        if not self.results.get('nodejs_version', True):
            requirements.append("Node.js 14.0 或更高版本")

        if not self.results.get('disk_space', True):
            requirements.append("至少 500MB 可用磁盘空间")

        if not self.results.get('network', True):
            requirements.append("可访问 GitHub 的网络连接")

        return requirements

    def is_ready(self) -> bool:
        """
        检查环境是否就绪

        Returns:
            所有检查都通过返回True，否则返回False
        """
        return all(self.results.values())


# 测试代码
if __name__ == '__main__':
    checker = EnvChecker()
    results = checker.check_all()

    print("\n检查结果:")
    for name, status in results.items():
        print(f"  {name}: {status}")

    print(f"\n环境就绪: {checker.is_ready()}")

    if not checker.is_ready():
        print("\n未满足的要求:")
        for req in checker.get_requirements():
            print(f"  - {req}")
