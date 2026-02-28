"""
OpenClaw安装器
负责下载、安装和配置OpenClaw
"""

import subprocess
import os
import sys
from typing import Optional, Callable
from utils.logger import get_logger
from utils.platform import Platform
from utils.downloader import Downloader
from .config import Config

class Installer:
    """OpenClaw安装器"""

    def __init__(self):
        """初始化安装器"""
        self.logger = get_logger()
        self.config = Config()
        self.downloader = Downloader()

        # OpenClaw的npm包信息
        self.npm_package = 'openclaw-cn'
        self.npm_registry = 'https://registry.npmjs.org/'

    def install(
        self,
        install_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int, int], None]] = None
    ) -> bool:
        """
        执行完整安装流程

        Args:
            install_dir: 安装目录（默认为全局安装）
            progress_callback: 进度回调 callback(stage, current, total)

        Returns:
            安装成功返回True，失败返回False
        """
        self.logger.info("开始OpenClaw安装流程...")

        stages = [
            ("检查环境", 1),
            ("下载OpenClaw", 2),
            ("执行安装", 3),
            ("安装依赖", 4),
            ("初始化配置", 5),
            ("验证安装", 6)
        ]

        total_stages = len(stages)

        # 阶段1: 检查环境
        self._update_progress(progress_callback, stages[0][0], 1, total_stages)
        if not self._check_environment():
            self.logger.error("环境检查失败，安装终止")
            return False

        # 阶段2: 下载OpenClaw
        self._update_progress(progress_callback, stages[1][0], 2, total_stages)
        if not self._download_openclaw():
            self.logger.error("下载OpenClaw失败，安装终止")
            return False

        # 阶段3: 执行安装
        self._update_progress(progress_callback, stages[2][0], 3, total_stages)
        if not self._execute_install(install_dir):
            self.logger.error("安装OpenClaw失败，安装终止")
            return False

        # 阶段4: 安装依赖
        self._update_progress(progress_callback, stages[3][0], 4, total_stages)
        if not self._install_dependencies():
            self.logger.warning("依赖安装失败，但OpenClaw可能仍可使用")

        # 阶段5: 初始化配置
        self._update_progress(progress_callback, stages[4][0], 5, total_stages)
        self._init_config()

        # 阶段6: 验证安装
        self._update_progress(progress_callback, stages[5][0], 6, total_stages)
        if not self._verify_install():
            self.logger.warning("安装验证失败，但OpenClaw可能已安装")
            # 不返回False，因为可能只是版本检查失败

        self.logger.info("OpenClaw安装流程完成")
        return True

    def _check_environment(self) -> bool:
        """检查环境是否满足要求"""
        self.logger.info("检查安装环境...")

        # 检查npm是否可用
        try:
            result = subprocess.run(
                ['npm', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.error("npm未安装或不可用")
                return False

            self.logger.info(f"npm版本: {result.stdout.strip()}")

        except FileNotFoundError:
            self.logger.error("npm未安装，请先安装Node.js")
            return False
        except Exception as e:
            self.logger.error(f"环境检查失败: {e}")
            return False

        return True

    def _download_openclaw(self) -> bool:
        """下载OpenClaw（通过npm）"""
        self.logger.info("准备下载OpenClaw...")

        try:
            # 检查是否能访问npm registry
            can_access = self.downloader.check_url(
                f"{self.npm_registry}{self.npm_package}"
            )

            if can_access:
                self.logger.info(f"✓ 可以访问npm registry")
                self.logger.info(f"将通过npm安装 {self.npm_package}")
                return True
            else:
                self.logger.warning(f"无法访问npm registry，尝试继续安装...")
                # 即使无法访问registry，也允许继续（可能是缓存问题）
                return True

        except Exception as e:
            self.logger.warning(f"下载准备失败，但尝试继续: {e}")
            return True  # 不阻止安装流程

    def _execute_install(self, install_dir: Optional[str] = None) -> bool:
        """
        执行OpenClaw安装

        Args:
            install_dir: 安装目录（None表示全局安装）

        Returns:
            安装成功返回True，失败返回False
        """
        self.logger.info("开始安装OpenClaw...")

        try:
            # 构建npm install命令
            cmd = ['npm', 'install', '-g', self.npm_package]

            # 如果指定了安装目录，添加--prefix参数
            if install_dir:
                os.makedirs(install_dir, exist_ok=True)
                cmd.extend(['--prefix', install_dir])
                self.logger.info(f"安装目录: {install_dir}")
            else:
                self.logger.info("全局安装模式")

            self.logger.info(f"执行命令: {' '.join(cmd)}")

            # 执行安装
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )

            # 检查结果
            if result.returncode == 0:
                self.logger.info("OpenClaw安装成功")

                # 保存安装路径到配置
                if install_dir:
                    self.config.set('paths.openclaw', install_dir)
                else:
                    # 获取npm全局安装路径
                    global_path = self._get_npm_global_path()
                    if global_path:
                        self.config.set('paths.openclaw', global_path)

                return True
            else:
                self.logger.error(f"安装失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("安装超时（超过5分钟）")
            return False
        except Exception as e:
            self.logger.error(f"安装失败: {e}")
            return False

    def _install_dependencies(self) -> bool:
        """安装额外依赖（如果需要）"""
        self.logger.info("检查额外依赖...")

        try:
            # OpenClaw通过npm自动安装依赖，这里无需额外操作
            self.logger.info("依赖已通过npm自动安装")
            return True

        except Exception as e:
            self.logger.warning(f"依赖检查失败: {e}")
            return False

    def _init_config(self):
        """初始化配置"""
        self.logger.info("初始化配置...")

        try:
            # 加载配置
            self.config.load()

            # 设置默认值
            if not self.config.get('openclaw.install_dir'):
                install_dir = self.config.get('paths.openclaw')
                if install_dir:
                    self.config.set('openclaw.install_dir', install_dir)

            # 保存配置
            self.config.save()

            self.logger.info("配置初始化完成")

        except Exception as e:
            self.logger.warning(f"配置初始化失败: {e}")

    def _verify_install(self) -> bool:
        """验证OpenClaw是否安装成功"""
        self.logger.info("验证OpenClaw安装...")

        try:
            # 检查openclaw-cn命令是否可用
            result = subprocess.run(
                ['openclaw-cn', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                version = result.stdout.strip()
                self.logger.info(f"✓ OpenClaw已安装，版本: {version}")

                # 保存版本信息
                self.config.set('openclaw.version', version)
                self.config.save()

                return True
            else:
                self.logger.warning(f"✗ 版本检查失败: {result.stderr}")
                return False

        except FileNotFoundError:
            self.logger.warning("✗ openclaw-cn命令未找到")
            return False
        except Exception as e:
            self.logger.warning(f"✗ 验证失败: {e}")
            return False

    def _get_npm_global_path(self) -> Optional[str]:
        """获取npm全局安装路径"""
        try:
            result = subprocess.run(
                ['npm', 'config', 'get', 'prefix'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                path = result.stdout.strip()
                self.logger.debug(f"npm全局路径: {path}")
                return path

        except Exception as e:
            self.logger.debug(f"获取npm路径失败: {e}")

        return None

    def _update_progress(
        self,
        callback: Optional[Callable[[str, int, int], None]],
        stage: str,
        current: int,
        total: int
    ):
        """更新进度"""
        if callback:
            try:
                callback(stage, current, total)
            except Exception as e:
                self.logger.warning(f"进度回调失败: {e}")

    def uninstall(self) -> bool:
        """
        卸载OpenClaw

        Returns:
            卸载成功返回True，失败返回False
        """
        self.logger.info("开始卸载OpenClaw...")

        try:
            # 使用npm卸载
            result = subprocess.run(
                ['npm', 'uninstall', '-g', self.npm_package],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                self.logger.info("OpenClaw卸载成功")
                return True
            else:
                self.logger.error(f"卸载失败: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"卸载失败: {e}")
            return False

    def update(self) -> bool:
        """
        更新OpenClaw到最新版本

        Returns:
            更新成功返回True，失败返回False
        """
        self.logger.info("开始更新OpenClaw...")

        try:
            # 使用npm更新
            result = subprocess.run(
                ['npm', 'update', '-g', self.npm_package],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.logger.info("OpenClaw更新成功")
                return self._verify_install()
            else:
                self.logger.error(f"更新失败: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"更新失败: {e}")
            return False


# 测试代码
if __name__ == '__main__':
    installer = Installer()

    # 测试环境检查
    print("测试环境检查...")
    if installer._check_environment():
        print("环境检查通过")
    else:
        print("环境检查失败")

    # 测试安装验证
    print("\n测试安装验证...")
    if installer._verify_install():
        print("OpenClaw已安装")
    else:
        print("OpenClaw未安装")
