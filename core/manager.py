"""
OpenClaw管理器
负责启动、停止、状态监控和Web界面管理
"""

import subprocess
import time
import webbrowser
from typing import Optional, Callable
from utils.logger import get_logger
from utils.platform import Platform
from .config import Config

class Manager:
    """OpenClaw管理器"""

    def __init__(self):
        """初始化管理器"""
        self.logger = get_logger()
        self.config = Config()

        # 进程信息
        self.process: Optional[subprocess.Popen] = None
        self.pid: Optional[int] = None
        self.port: Optional[int] = None

        # 状态
        self.is_running = False

    def start(
        self,
        port: Optional[int] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        启动OpenClaw

        Args:
            port: 端口号（None则使用配置中的端口）
            callback: 状态回调函数

        Returns:
            启动成功返回True，失败返回False
        """
        if self.is_running:
            self.logger.warning("OpenClaw已在运行")
            return False

        self.logger.info("启动OpenClaw...")
        self._log_callback(callback, "正在启动OpenClaw...")

        try:
            # 获取端口
            if port is None:
                port = self.config.get('openclaw.port', 3000)

            self.port = port
            self._log_callback(callback, f"使用端口: {port}")

            # 构建启动命令
            cmd = ['openclaw-cn', 'gateway', 'start']

            self.logger.info(f"执行命令: {' '.join(cmd)}")

            # 启动进程
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 获取PID
            self.pid = self.process.pid
            self._log_callback(callback, f"进程PID: {self.pid}")

            # 等待启动（检查进程是否还在运行）
            time.sleep(1)

            if self.process.poll() is None:
                # 进程仍在运行，启动成功
                self.is_running = True
                self.logger.info(f"✓ OpenClaw启动成功 (PID: {self.pid})")
                self._log_callback(callback, "✓ OpenClaw启动成功")

                # 保存配置
                self.config.set('openclaw.port', port)
                self.config.save()

                return True
            else:
                # 进程已退出，启动失败
                returncode = self.process.returncode
                stderr = self.process.stderr.read()

                self.logger.error(f"✗ OpenClaw启动失败 (返回码: {returncode})")
                self.logger.error(f"错误信息: {stderr}")

                self._log_callback(callback, f"✗ 启动失败: {stderr}")

                # 清理
                self.process = None
                self.pid = None

                return False

        except FileNotFoundError:
            self.logger.error("✗ openclaw-cn命令未找到")
            self._log_callback(callback, "✗ openclaw-cn未安装")
            return False

        except Exception as e:
            self.logger.error(f"✗ 启动失败: {e}")
            self._log_callback(callback, f"✗ 启动失败: {e}")
            return False

    def stop(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        停止OpenClaw

        Args:
            callback: 状态回调函数

        Returns:
            停止成功返回True，失败返回False
        """
        if not self.is_running:
            self.logger.warning("OpenClaw未运行")
            return False

        self.logger.info("停止OpenClaw...")
        self._log_callback(callback, "正在停止OpenClaw...")

        try:
            if self.process:
                # 尝试优雅终止
                self.process.terminate()

                # 等待最多5秒
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # 超时则强制终止
                    self.logger.warning("优雅终止超时，强制终止")
                    self.process.kill()
                    self.process.wait()

                self.is_running = False
                self.process = None
                self.pid = None

                self.logger.info("✓ OpenClaw已停止")
                self._log_callback(callback, "✓ OpenClaw已停止")

                return True

        except Exception as e:
            self.logger.error(f"✗ 停止失败: {e}")
            self._log_callback(callback, f"✗ 停止失败: {e}")
            return False

        return False

    def restart(self, callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        重启OpenClaw

        Args:
            callback: 状态回调函数

        Returns:
            重启成功返回True，失败返回False
        """
        self.logger.info("重启OpenClaw...")
        self._log_callback(callback, "正在重启OpenClaw...")

        # 先停止
        if self.is_running:
            self.stop(callback)
            time.sleep(1)

        # 再启动
        return self.start(callback=callback)

    def get_status(self) -> dict:
        """
        获取OpenClaw运行状态

        Returns:
            状态字典
        """
        status = {
            'running': self.is_running,
            'pid': self.pid,
            'port': self.port,
            'version': None,
            'uptime': None
        }

        if self.is_running and self.process:
            # 检查进程是否仍在运行
            if self.process.poll() is None:
                # 进程仍在运行
                status['pid'] = self.process.pid
            else:
                # 进程已退出
                self.is_running = False
                self.process = None
                self.pid = None
                status['running'] = False

        # 尝试获取版本
        try:
            result = subprocess.run(
                ['openclaw-cn', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                status['version'] = result.stdout.strip()
        except:
            pass

        return status

    def open_webui(
        self,
        url: Optional[str] = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        打开Web界面

        Args:
            url: Web界面URL（None则自动构建）
            callback: 状态回调函数

        Returns:
            成功返回True，失败返回False
        """
        self.logger.info("打开Web界面...")
        self._log_callback(callback, "正在打开Web界面...")

        try:
            # 构建URL
            if url is None:
                port = self.port or self.config.get('openclaw.port', 3000)
                url = f"http://localhost:{port}"

            self.logger.info(f"打开URL: {url}")

            # 打开浏览器
            webbrowser.open(url)

            self.logger.info(f"✓ 已打开Web界面: {url}")
            self._log_callback(callback, f"✓ 已打开Web界面: {url}")

            return True

        except Exception as e:
            self.logger.error(f"✗ 打开Web界面失败: {e}")
            self._log_callback(callback, f"✗ 打开失败: {e}")
            return False

    def is_running(self) -> bool:
        """检查OpenClaw是否运行中"""
        if not self.is_running:
            return False

        if self.process and self.process.poll() is None:
            return True

        # 进程已退出
        self.is_running = False
        return False

    def get_logs(self, lines: int = 100) -> Optional[str]:
        """
        获取OpenClaw日志

        Args:
            lines: 读取行数

        Returns:
            日志内容，失败返回None
        """
        self.logger.info(f"获取OpenClaw日志 (最近{lines}行)...")

        try:
            result = subprocess.run(
                ['openclaw-cn', 'gateway', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout
            else:
                self.logger.warning(f"获取日志失败: {result.stderr}")
                return None

        except Exception as e:
            self.logger.error(f"获取日志失败: {e}")
            return None

    def _log_callback(
        self,
        callback: Optional[Callable[[str], None]],
        message: str
    ):
        """调用回调函数记录日志"""
        if callback:
            try:
                callback(message)
            except Exception as e:
                self.logger.warning(f"回调函数调用失败: {e}")


# 测试代码
if __name__ == '__main__':
    manager = Manager()

    # 测试获取状态
    print("测试获取状态...")
    status = manager.get_status()
    print(f"状态: {status}")

    # 测试打开Web界面
    print("\n测试打开Web界面...")
    if manager.open_webui():
        print("Web界面已打开")
    else:
        print("打开失败")
