#!/usr/bin/env python3
"""
OpenClaw 简易安装器 v3.0
- 简单的 GUI 启动器
- 分 Mac/Win 两个标签页
- 直接执行终端命令
- 分步骤安装：检查依赖 → 安装 Node.js → 安装 OpenClaw
- 日志直接显示终端内容
"""

import subprocess
import threading
import sys
import os
from tkinter import messagebox

# 尝试导入 tkinter（GUI 模式）
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    print("⚠️  Tkinter 未安装，请安装 Python 的 tkinter 模块")

# 导入平台检测
try:
    from utils.platform import Platform
except ImportError:
    import platform
    class Platform:
        @staticmethod
        def is_windows():
            return platform.system() == 'Windows'
        @staticmethod
        def is_macos():
            return platform.system() == 'Darwin'

class OpenClawInstaller:
    """OpenClaw 简易安装器"""
    
    def __init__(self, root: tk.Tk):
        """初始化安装器"""
        self.root = root
        self.setup_window()
        self.create_ui()
        
    def setup_window(self):
        """设置窗口"""
        self.root.title("OpenClaw 安装器")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        
        # 窗口居中
        self.center_window()
        
    def center_window(self):
        """窗口居中"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_ui(self):
        """创建 UI"""
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="OpenClaw 安装器",
            font=('Helvetica', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 平台选择（标签页）
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 检测当前平台
        current_platform = "macos" if Platform.is_macos() else "windows"
        
        # 创建标签页
        self.macos_page = self.create_macos_page(notebook)
        self.windows_page = self.create_windows_page(notebook)
        
        # 添加到标签页
        notebook.add(self.macos_page, text="macOS")
        notebook.add(self.windows_page, text="Windows")
        
        # 默认选中当前平台
        if current_platform == "macos":
            notebook.select(0)
        else:
            notebook.select(1)
    
    def create_macos_page(self, parent: ttk.Frame) -> ttk.Frame:
        """创建 macOS 页面"""
        frame = ttk.Frame(parent)
        
        # 说明
        desc_label = ttk.Label(
            frame,
            text="macOS 安装",
            font=('Helvetica', 14, 'bold')
        )
        desc_label.pack(pady=10)
        
        # 系统要求
        req_frame = ttk.LabelFrame(frame, text="系统要求")
        req_frame.pack(fill=tk.X, padx=10, pady=10)
        
        reqs = [
            "• macOS 10.13 或更高版本",
            "• 至少 500MB 可用磁盘空间",
            "• 可访问互联网（下载依赖）"
        ]
        
        for req in reqs:
            req_label = ttk.Label(req_frame, text=req)
            req_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        # 检查环境按钮
        self.macos_check_btn = ttk.Button(
            btn_frame,
            text="检查依赖环境",
            command=lambda: self.check_macos_environment()
        )
        self.macos_check_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 安装 Node.js 按钮
        self.macos_node_btn = ttk.Button(
            btn_frame,
            text="安装 Node.js",
            command=lambda: self.install_macos_nodejs()
        )
        self.macos_node_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 安装 OpenClaw 按钮
        self.macos_install_btn = ttk.Button(
            btn_frame,
            text="安装 OpenClaw",
            command=lambda: self.install_macos_openclaw()
        )
        self.macos_install_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 终端输出
        terminal_frame = ttk.LabelFrame(frame, text="终端输出")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        self.macos_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=15,
            wrap=tk.NONE,
            state='disabled',
            font=('Consolas', 10)
        )
        self.macos_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(self.macos_output, orient=tk.HORIZONTAL, command=self.macos_output.xview)
        self.macos_output['xscrollcommand'] = h_scrollbar.set
        
        return frame
    
    def create_windows_page(self, parent: ttk.Frame) -> ttk.Frame:
        """创建 Windows 页面"""
        frame = ttk.Frame(parent)
        
        # 说明
        desc_label = ttk.Label(
            frame,
            text="Windows 安装",
            font=('Helvetica', 14, 'bold')
        )
        desc_label.pack(pady=10)
        
        # 系统要求
        req_frame = ttk.LabelFrame(frame, text="系统要求")
        req_frame.pack(fill=tk.X, padx=10, pady=10)
        
        reqs = [
            "• Windows 10 或更高版本",
            "• 至少 500MB 可用磁盘空间",
            "• 可访问互联网（下载依赖）"
        ]
        
        for req in reqs:
            req_label = ttk.Label(req_frame, text=req)
            req_label.pack(anchor=tk.W, padx=10, pady=2)
        
        # 按钮区域
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=20)
        
        # 检查环境按钮
        self.windows_check_btn = ttk.Button(
            btn_frame,
            text="检查依赖环境",
            command=lambda: self.check_windows_environment()
        )
        self.windows_check_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 安装 Node.js 按钮
        self.windows_node_btn = ttk.Button(
            btn_frame,
            text="安装 Node.js",
            command=lambda: self.install_windows_nodejs()
        )
        self.windows_node_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 安装 OpenClaw 按钮
        self.windows_install_btn = ttk.Button(
            btn_frame,
            text="安装 OpenClaw",
            command=lambda: self.install_windows_openclaw()
        )
        self.windows_install_btn.pack(ipadx=15, ipady=5, pady=5)
        
        # 终端输出
        terminal_frame = ttk.LabelFrame(frame, text="终端输出")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
        
        self.windows_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=15,
            wrap=tk.NONE,
            state='disabled',
            font=('Consolas', 10)
        )
        self.windows_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 添加水平滚动条
        h_scrollbar = ttk.Scrollbar(self.windows_output, orient=tk.HORIZONTAL, command=self.windows_output.xview)
        self.windows_output['xscrollcommand'] = h_scrollbar.set
        
        return frame
    
    # ===== macOS 方法 =====
    
    def check_macos_environment(self):
        """检查 macOS 环境"""
        self.macos_output.config(state='normal')
        self.macos_output.delete(1.0, tk.END)
        self.macos_output.insert(tk.END, "检查 macOS 依赖环境...\n\n")
        
        thread = threading.Thread(target=self._check_macos_environment)
        thread.daemon = True
        thread.start()
    
    def _check_macos_environment(self):
        """执行 macOS 环境检查"""
        commands = [
            ("系统版本", "sw_vers"),
            ("Homebrew", "command -v brew && brew --version || echo 'Homebrew 未安装'"),
            ("Node.js", "command -v node && node --version || echo 'Node.js 未安装'"),
            ("npm", "command -v npm && npm --version || echo 'npm 未安装'"),
            ("磁盘空间", "df -h / | tail -1 | awk '{print \"可用空间: \" $4}'"),
        ]
        
        for name, cmd in commands:
            self.log_to_macos(f"\n{'='*60}\n{name}\n{'='*60}\n")
            self.run_command_macos(cmd)
        
        self.log_to_macos(f"\n{'='*60}\n✓ 环境检查完成\n{'='*60}\n")
    
    def install_macos_nodejs(self):
        """安装 macOS Node.js"""
        self.macos_output.config(state='normal')
        self.macos_output.delete(1.0, tk.END)
        self.macos_output.insert(tk.END, "安装 Node.js (macOS)...\n\n")
        
        thread = threading.Thread(target=self._install_macos_nodejs)
        thread.daemon = True
        thread.start()
    
    def _install_macos_nodejs(self):
        """执行 macOS Node.js 安装"""
        # 先检查 Homebrew
        self.log_to_macos(f"{'='*60}\n检查 Homebrew\n{'='*60}\n")
        self.run_command_macos("command -v brew && echo 'Homebrew 已安装' || echo 'Homebrew 未安装'")
        
        # 如果没有 Homebrew，提示先安装
        self.log_to_macos(f"\n{'='*60}\n安装 Homebrew\n{'='*60}\n")
        self.run_command_macos("""
        if ! command -v brew; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        else
            echo "Homebrew 已存在"
        fi
        """)
        
        # 安装 Node.js
        self.log_to_macos(f"\n{'='*60}\n安装 Node.js\n{'='*60}\n")
        self.run_command_macos("""
        if ! command -v node; then
            brew install node
        else
            echo "Node.js 已安装"
        fi
        """)
        
        # 验证
        self.log_to_macos(f"\n{'='*60}\n验证安装\n{'='*60}\n")
        self.run_command_macos("node --version && npm --version")
        
        self.log_to_macos(f"\n{'='*60}\n✓ Node.js 安装完成\n{'='*60}\n")
    
    def install_macos_openclaw(self):
        """安装 macOS OpenClaw"""
        self.macos_output.config(state='normal')
        self.macos_output.delete(1.0, tk.END)
        self.macos_output.insert(tk.END, "安装 OpenClaw (macOS)...\n\n")
        
        thread = threading.Thread(target=self._install_macos_openclaw)
        thread.daemon = True
        thread.start()
    
    def _install_macos_openclaw(self):
        """执行 macOS OpenClaw 安装"""
        self.log_to_macos(f"{'='*60}\n安装 OpenClaw\n{'='*60}\n")
        self.run_command_macos("npm install -g openclaw-cn")
        
        self.log_to_macos(f"\n{'='*60}\n验证安装\n{'='*60}\n")
        self.run_command_macos("openclaw-cn --version")
        
        self.log_to_macos(f"\n{'='*60}\n✓ OpenClaw 安装完成\n{'='*60}\n")
        self.log_to_macos("\n使用方法:\n")
        self.log_to_macos("  openclaw-cn gateway start    # 启动服务\n")
        self.log_to_macos("  openclaw-cn gateway stop     # 停止服务\n")
        self.log_to_macos("  openclaw-cn --help          # 查看帮助\n")
    
    def run_command_macos(self, cmd):
        """运行 macOS 命令"""
        try:
            process = subprocess.Popen(
                ['/bin/zsh', '-c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # 实时输出
            for line in process.stdout:
                self.log_to_macos(line)
            
            process.wait()
            
        except Exception as e:
            self.log_to_macos(f"错误: {e}\n")
    
    def log_to_macos(self, text):
        """记录到 macOS 输出"""
        self.root.after(0, lambda: self.macos_output.insert(tk.END, text))
        self.root.after(0, lambda: self.macos_output.see(tk.END))
    
    # ===== Windows 方法 =====
    
    def check_windows_environment(self):
        """检查 Windows 环境"""
        self.windows_output.config(state='normal')
        self.windows_output.delete(1.0, tk.END)
        self.windows_output.insert(tk.END, "检查 Windows 依赖环境...\n\n")
        
        thread = threading.Thread(target=self._check_windows_environment)
        thread.daemon = True
        thread.start()
    
    def _check_windows_environment(self):
        """执行 Windows 环境检查"""
        commands = [
            ("系统版本", "ver"),
            ("Node.js", "node --version || echo Node.js 未安装"),
            ("npm", "npm --version || echo npm 未安装"),
        ]
        
        for name, cmd in commands:
            self.log_to_windows(f"\n{'='*60}\n{name}\n{'='*60}\n")
            self.run_command_windows(cmd)
        
        self.log_to_windows(f"\n{'='*60}\n✓ 环境检查完成\n{'='*60}\n")
    
    def install_windows_nodejs(self):
        """安装 Windows Node.js"""
        self.windows_output.config(state='normal')
        self.windows_output.delete(1.0, tk.END)
        self.windows_output.insert(tk.END, "安装 Node.js (Windows)...\n\n")
        
        thread = threading.Thread(target=self._install_windows_nodejs)
        thread.daemon = True
        thread.start()
    
    def _install_windows_nodejs(self):
        """执行 Windows Node.js 安装"""
        self.log_to_windows(f"{'='*60}\n使用 winget 安装 Node.js\n{'='*60}\n")
        
        # 尝试使用 winget 安装
        self.run_command_windows("winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements")
        
        # 验证
        self.log_to_windows(f"\n{'='*60}\n验证安装\n{'='*60}\n")
        self.run_command_windows("node --version && npm --version")
        
        self.log_to_windows(f"\n{'='*60}\n✓ Node.js 安装完成\n{'='*60}\n")
        
        # 如果 winget 不可用，提示手动安装
        self.root.after(0, lambda: messagebox.showinfo(
            "安装提示",
            "如果 winget 不可用，请手动安装：\n\n"
            "1. 访问 https://nodejs.org/\n"
            "2. 下载 Node.js LTS 版本\n"
            "3. 安装完成后重新点击'检查依赖环境'"
        ))
    
    def install_windows_openclaw(self):
        """安装 Windows OpenClaw"""
        self.windows_output.config(state='normal')
        self.windows_output.delete(1.0, tk.END)
        self.windows_output.insert(tk.END, "安装 OpenClaw (Windows)...\n\n")
        
        thread = threading.Thread(target=self._install_windows_openclaw)
        thread.daemon = True
        thread.start()
    
    def _install_windows_openclaw(self):
        """执行 Windows OpenClaw 安装"""
        self.log_to_windows(f"{'='*60}\n安装 OpenClaw\n{'='*60}\n")
        self.run_command_windows("npm install -g openclaw-cn")
        
        self.log_to_windows(f"\n{'='*60}\n验证安装\n{'='*60}\n")
        self.run_command_windows("openclaw-cn --version")
        
        self.log_to_windows(f"\n{'='*60}\n✓ OpenClaw 安装完成\n{'='*60}\n")
        self.log_to_windows("\n使用方法:\n")
        self.log_to_windows("  openclaw-cn gateway start    # 启动服务\n")
        self.log_to_windows("  openclaw-cn gateway stop     # 停止服务\n")
        self.log_to_windows("  openclaw-cn --help          # 查看帮助\n")
    
    def run_command_windows(self, cmd):
        """运行 Windows 命令"""
        try:
            process = subprocess.Popen(
                ['cmd.exe', '/c', cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # 实时输出
            for line in process.stdout:
                self.log_to_windows(line)
            
            process.wait()
            
        except Exception as e:
            self.log_to_windows(f"错误: {e}\n")
    
    def log_to_windows(self, text):
        """记录到 Windows 输出"""
        self.root.after(0, lambda: self.windows_output.insert(tk.END, text))
        self.root.after(0, lambda: self.windows_output.see(tk.END))
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()


if __name__ == '__main__':
    if not HAS_TKINTER:
        print("错误：tkinter 模块未安装")
        print("请安装 tkinter：")
        print("  macOS: brew install python-tk@3.11")
        print("  Ubuntu: sudo apt install python3-tk")
        print("  Windows: 重新安装 Python 时勾选 tcl/tk")
        sys.exit(1)
    
    root = tk.Tk()
    app = OpenClawInstaller(root)
    app.run()
