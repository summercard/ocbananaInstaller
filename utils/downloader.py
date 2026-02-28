"""
下载工具
支持文件下载和进度显示
"""

import os
import requests
from typing import Optional, Callable
from .logger import get_logger

class Downloader:
    """下载管理类"""

    def __init__(self):
        """初始化下载器"""
        self.logger = get_logger()

    def download(
        self,
        url: str,
        dest_path: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        下载文件

        Args:
            url: 下载URL
            dest_path: 目标路径
            progress_callback: 进度回调函数 callback(downloaded, total)

        Returns:
            下载成功返回True，失败返回False
        """
        try:
            # 创建目标目录
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            # 下载文件
            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            # 写入文件
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # 调用进度回调
                        if progress_callback:
                            progress_callback(downloaded, total_size)

            self.logger.info(f"文件下载成功: {dest_path}")
            return True

        except Exception as e:
            self.logger.error(f"文件下载失败: {e}")
            # 删除可能已下载的部分文件
            if os.path.exists(dest_path):
                try:
                    os.remove(dest_path)
                except:
                    pass
            return False

    def download_text(self, url: str) -> Optional[str]:
        """
        下载文本内容

        Args:
            url: 下载URL

        Returns:
            文本内容，失败返回None
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.logger.error(f"文本下载失败: {e}")
            return None

    def download_json(self, url: str) -> Optional[dict]:
        """
        下载JSON数据

        Args:
            url: 下载URL

        Returns:
            JSON数据，失败返回None
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"JSON下载失败: {e}")
            return None

    def check_url(self, url: str) -> bool:
        """
        检查URL是否可访问

        Args:
            url: 要检查的URL

        Returns:
            可访问返回True，否则返回False
        """
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.debug(f"URL检查失败: {e}")
            return False

# 测试代码
if __name__ == '__main__':
    downloader = Downloader()

    # 测试下载
    def progress(downloaded, total):
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\r下载进度: {percent:.1f}% ({downloaded}/{total})", end='')
        else:
            print(f"\r已下载: {downloaded} bytes", end='')

    print("开始下载测试...")
    url = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    dest = "/tmp/test_download.txt"

    if downloader.download(url, dest, progress):
        print(f"\n下载成功: {dest}")
        print(f"文件大小: {os.path.getsize(dest)} bytes")
    else:
        print("\n下载失败")
