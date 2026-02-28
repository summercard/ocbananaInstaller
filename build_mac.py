#!/usr/bin/env python3
"""
macOS 平台打包脚本
将 OpenClaw 安装器打包成 .app 应用程序
"""

import os
import platform
import subprocess
import shutil
import sys


def clean_build():
    """清理之前的构建目录"""
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"清理目录: {d}")
            shutil.rmtree(d)


def convert_icon():
    """将 PNG 图标转换为 macOS 需要的 ICNS 格式"""
    icon_path = 'image/icon.png'
    icns_path = 'image/icon.icns'

    if not os.path.exists(icon_path):
        print(f"警告: 找不到图标文件 {icon_path}")
        return None

    # 检查 icns 是否已存在且是最新的
    if os.path.exists(icns_path):
        if os.path.getmtime(icns_path) > os.path.getmtime(icon_path):
            print("使用已有的 .icns")
            return icns_path

    # 尝试使用 iconutil 转换
    # 先创建 iconset 目录
    iconset_dir = 'image/icon.iconset'
    if os.path.exists(iconset_dir):
        shutil.rmtree(iconset_dir)
    os.makedirs(iconset_dir)

    # 复制不同尺寸的图片
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    try:
        from PIL import Image
        img = Image.open(icon_path)

        for size in sizes:
            # @2x 版本
            img.resize((size * 2, size * 2)).save(f'{iconset_dir}/icon_{size}x{size}.png')
            # 普通版本
            img.resize((size, size)).save(f'{iconset_dir}/icon_{size}x{size}@2x.png')

        # 使用 iconutil 转换为 icns
        subprocess.run(['iconutil', '-c', 'icns', '-o', icns_path, iconset_dir], check=True)
        print(f"已转换图标: {icns_path}")

        # 清理 iconset
        shutil.rmtree(iconset_dir)

        return icns_path
    except Exception as e:
        print(f"图标转换失败: {e}")
        return None


def build_macos():
    """macOS 平台打包"""
    print("开始打包 macOS 版本...")

    # 转换图标
    icon_path = convert_icon()

    # 构建 pyinstaller 命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=OpenClawInstaller',
        '--onedir',  # 打包成目录模式（兼容性更好）
        '--noconsole',  # 无控制台窗口
        '--osx-bundle-identifier=com.openclaw.installer',
    ]

    # 添加图标
    if icon_path:
        cmd.extend(['--icon', icon_path])

    # 添加图片资源文件 (macOS 使用冒号)
    if os.path.exists('image/002.png'):
        cmd.extend(['--add-data', 'image/002.png:image'])
    if os.path.exists('image/icon.png'):
        cmd.extend(['--add-data', 'image/icon.png:image'])

    # 添加主程序
    cmd.append('simple_installer.py')

    # 执行打包
    print(f"执行命令: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    # 移动到 app 目录
    app_path = 'dist/OpenClawInstaller.app'
    if os.path.exists(app_path):
        print(f"\n打包完成！")
        print(f"App 位置: {os.path.abspath(app_path)}")
        print(f"\n你可以:")
        print(f"  1. 双击运行: open {app_path}")
        print(f"  2. 复制到应用程序: cp -r {app_path} /Applications/")
    else:
        print("错误: 打包失败，未找到 app 文件")


if __name__ == "__main__":
    if platform.system() != 'Darwin':
        print("警告: 此脚本建议在 macOS 上运行")

    clean_build()
    build_macos()
