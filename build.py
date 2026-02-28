"""
OpenClawInstaller打包脚本
使用PyInstaller打包成独立可执行文件
"""

import os
import subprocess
import shutil
from utils.logger import get_logger

class Builder:
    """打包器"""

    def __init__(self):
        """初始化打包器"""
        self.logger = get_logger()
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.dist_dir = os.path.join(self.project_dir, 'dist')
        self.build_dir = os.path.join(self.project_dir, 'build')

    def build(self, platform: str = None):
        """
        执行打包

        Args:
            platform: 目标平台（None表示当前平台）
        """
        self.logger.info("开始打包...")

        # 清理旧的打包文件
        self._clean()

        # 构建PyInstaller命令
        cmd = self._build_command(platform)

        self.logger.info(f"执行命令: {' '.join(cmd)}")

        # 执行打包
        try:
            subprocess.run(cmd, check=True)
            self.logger.info("✓ 打包成功")
            self.logger.info(f"输出目录: {self.dist_dir}")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"✗ 打包失败: {e}")
            return False

    def _build_command(self, platform: str) -> list:
        """
        构建PyInstaller命令

        Args:
            platform: 目标平台

        Returns:
            命令列表
        """
        cmd = [
            'pyinstaller',
            '--name=OpenClawInstaller',
            '--windowed',  # GUI应用，不显示控制台
            '--onefile',  # 打包成单个文件
            '--clean',  # 清理临时文件
            '--noconfirm',  # 不询问确认
            'main.py'
        ]

        # 添加数据文件（如果有）
        # cmd.extend([
        #     '--add-data=config.json:config',
        #     '--add-data=templates:templates'
        # ])

        # 添加图标（如果有）
        icon_path = os.path.join(self.project_dir, 'icon.ico')
        if os.path.exists(icon_path):
            cmd.extend([f'--icon={icon_path}'])

        return cmd

    def _clean(self):
        """清理旧的打包文件"""
        self.logger.info("清理旧的打包文件...")

        for dir_path in [self.dist_dir, self.build_dir]:
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)
                self.logger.info(f"已删除: {dir_path}")

        # 清理spec文件
        spec_files = [f for f in os.listdir(self.project_dir) if f.endswith('.spec')]
        for spec_file in spec_files:
            os.remove(os.path.join(self.project_dir, spec_file))
            self.logger.info(f"已删除: {spec_file}")

    def build_dev(self):
        """开发模式打包（带控制台）"""
        self.logger.info("开始开发模式打包...")

        cmd = [
            'pyinstaller',
            '--name=OpenClawInstaller-Dev',
            '--onefile',
            '--clean',
            '--noconfirm',
            'main.py'
        ]

        try:
            subprocess.run(cmd, check=True)
            self.logger.info("✓ 开发模式打包成功")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"✗ 打包失败: {e}")
            return False


# 命令行入口
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='OpenClawInstaller打包工具')
    parser.add_argument('--dev', action='store_true', help='开发模式（带控制台）')
    parser.add_argument('--clean', action='store_true', help='仅清理不打包')

    args = parser.parse_args()

    builder = Builder()

    if args.clean:
        builder._clean()
    elif args.dev:
        builder.build_dev()
    else:
        builder.build()
