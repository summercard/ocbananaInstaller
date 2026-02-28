"""
OpenClaw跨平台安装工具
主入口文件
"""

import tkinter as tk
from gui.main_window import MainWindow
from utils.logger import get_logger
import sys

def main():
    """主函数"""
    # 初始化日志
    logger = get_logger()
    logger.info("OpenClaw跨平台安装工具启动")

    # 创建主窗口
    root = tk.Tk()

    # 创建应用实例
    app = MainWindow(root)

    # 运行主循环
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常退出: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("OpenClaw跨平台安装工具退出")

if __name__ == '__main__':
    main()
