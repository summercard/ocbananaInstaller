#!/usr/bin/env python3
"""
OpenClaw 安装器启动器（简单版）
只负责启动主安装器，不包含其他功能
"""

import subprocess
import sys
import os

def main():
    """启动主安装器"""
    # 获取当前脚本所在目录
    if getattr(sys, 'frozen', False):
        # 打包后的 .exe
        current_dir = os.path.dirname(sys.executable)
    else:
        # 开发模式
        current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 主安装器脚本路径
    installer_script = os.path.join(current_dir, "simple_installer.py")
    
    # 检查安装器脚本是否存在
    if not os.path.exists(installer_script):
        print("错误：找不到 simple_installer.py")
        print(f"预期路径：{installer_script}")
        print("\n请确保 simple_installer.py 和启动器在同一目录下。")
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 启动主安装器
    try:
        # 使用 Python 解释器运行
        subprocess.run(
            [sys.executable, installer_script],
            cwd=current_dir,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"\n错误：安装器运行失败，返回码：{e.returncode}")
        input("\n按回车键退出...")
        sys.exit(1)
    except FileNotFoundError:
        print("\n错误：找不到 Python 解释器")
        print("\n请确保已安装 Python 3.10 或更高版本。")
        input("\n按回车键退出...")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n用户取消安装。")
        sys.exit(0)
    except Exception as e:
        print(f"\n错误：{e}")
        input("\n按回车键退出...")
        sys.exit(1)

if __name__ == '__main__':
    main()
