import os
import platform
import subprocess
import shutil

def clean_build():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"清理目录: {d}")
            shutil.rmtree(d)

def build_windows():
    """Windows 平台打包"""
    print("开始打包 Windows 版本...")
    
    cmd = [
        'C:/Users/zhuangmenghong/AppData/Local/Programs/Python/Python311/Scripts/pyinstaller.exe',
        '--name=OpenClawInstaller',
        '--windowed',  # 无控制台窗口
        '--onefile',   # 打包成单文件
        '--icon=image/icon.png', # 设置执行文件图标
        # 添加图片资源文件，注意 Windows 下的分隔符是分号 ;
        '--add-data=image/002.png;image',
        '--add-data=image/icon.png;image',
        'simple_installer.py'
    ]
    
    # 执行打包
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    print("打包完成！产物位于 dist 目录中。")

if __name__ == "__main__":
    if platform.system() != 'Windows':
        print("错误：此脚本当前仅用于本地 Windows 打包。")
        exit(1)
        
    clean_build()
    build_windows()
