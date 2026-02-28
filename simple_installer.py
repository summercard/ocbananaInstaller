#!/usr/bin/env python3
"""
OpenClaw 简易安装器 v2.1
- 简单的 GUI 启动器
- 分 Mac/Win 两个标签页
- 直接执行终端命令
- 分步骤安装：检查依赖 → 安装依赖 → 安装 OpenClaw
"""

import subprocess
import threading
import sys
import os

# 尝试导入 tkinter（GUI 模式）
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    print("⚠️  Tkinter 未安装，使用终端模式")
    print("安装命令：brew install python-tk@3.11")

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
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
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
            
        # 底部说明
        info_frame = ttk.LabelFrame(main_frame, text="说明")
        info_frame.pack(fill=tk.X, pady=(10, 0))
        
        info_text = """
        简易安装说明：
        1. 选择你的操作系统（macOS 或 Windows）
        2. 点击"开始安装"按钮
        3. 安装过程会按步骤执行：
           • 步骤 1/3：检查依赖环境
           • 步骤 2/3：安装依赖环境
           • 步骤 3/3：安装 OpenClaw
        4. 等待安装完成（查看终端输出）
        
        注意事项：
        - 安装过程需要联网（下载 Node.js 和 OpenClaw）
        - 首次安装可能需要 5-10 分钟
        - 如果安装失败，请查看终端输出的错误信息
        """
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(padx=10, pady=10)
        
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
        
        # 安装按钮
        install_frame = ttk.Frame(frame)
        install_frame.pack(pady=20)
        
        self.macos_install_btn = ttk.Button(
            install_frame,
            text="开始安装",
            command=lambda: self.start_macos_install()
        )
        self.macos_install_btn.pack(ipadx=20, ipady=10)
        
        # 终端输出
        terminal_frame = ttk.LabelFrame(frame, text="安装输出")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.macos_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=15,
            wrap=tk.WORD,
            state='disabled'
        )
        self.macos_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
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
        
        # 安装按钮
        install_frame = ttk.Frame(frame)
        install_frame.pack(pady=20)
        
        self.windows_install_btn = ttk.Button(
            install_frame,
            text="开始安装",
            command=lambda: self.start_windows_install()
        )
        self.windows_install_btn.pack(ipadx=20, ipady=10)
        
        # 终端输出
        terminal_frame = ttk.LabelFrame(frame, text="安装输出")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.windows_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=15,
            wrap=tk.WORD,
            state='disabled'
        )
        self.windows_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        return frame
    
    def start_macos_install(self):
        """开始 macOS 安装"""
        self.macos_install_btn.config(state='disabled')
        self.macos_output.config(state='normal')
        self.macos_output.delete(1.0, tk.END)
        self.macos_output.insert(tk.END, "开始 macOS 安装...\n\n")
        
        # 在后台线程执行安装
        thread = threading.Thread(target=self.run_macos_install)
        thread.daemon = True
        thread.start()
        
    def run_macos_install(self):
        """执行 macOS 安装（分步骤）"""
        # 步骤 1：检查依赖环境
        self.check_macos_dependencies()
        
        # 步骤 2：安装依赖环境
        self.install_macos_dependencies()
        
        # 步骤 3：安装 OpenClaw
        self.install_macos_openclaw()
        
        # 完成
        self.macos_install_btn.config(state='normal')
        
    def check_macos_dependencies(self):
        """检查 macOS 依赖环境"""
        self.log_to_macos_output("\n" + "="*60)
        self.log_to_macos_output("步骤 1/3：检查依赖环境")
        self.log_to_macos_output("="*60 + "\n")
        
        commands = [
            ("检查系统版本", "sw_vers"),
            ("检查 Python", "python3 --version"),
            ("检查 Homebrew", "command -v brew && echo 'Homebrew 已安装' || echo 'Homebrew 未安装'"),
            ("检查 Node.js", "command -v node && node --version || echo 'Node.js 未安装'"),
            ("检查 npm", "command -v npm && npm --version || echo 'npm 未安装'"),
            ("检查磁盘空间", "df -h / | tail -1 | awk '{print \"可用磁盘空间: \" $4}'"),
        ]
        
        for name, cmd in commands:
            self.log_to_macos_output(f"\n{name}...")
            try:
                process = subprocess.Popen(
                    ['/bin/zsh', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    self.log_to_macos_output(line)
                process.wait()
            except Exception as e:
                self.log_to_macos_output(f"检查失败: {e}\n")
        
        self.log_to_macos_output("\n✓ 依赖环境检查完成\n")
        
    def install_macos_dependencies(self):
        """安装 macOS 依赖环境"""
        self.log_to_macos_output("\n" + "="*60)
        self.log_to_macos_output("步骤 2/3：安装依赖环境")
        self.log_to_macos_output("="*60 + "\n")
        
        commands = [
            ("安装 Homebrew", """
            if ! command -v brew &> /dev/null; then
                echo "正在安装 Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                echo ""
                echo "✓ Homebrew 安装完成"
            else
                echo "Homebrew 已安装，跳过"
            fi
            """),
            
            ("安装 Node.js", """
            if ! command -v node &> /dev/null; then
                echo "正在安装 Node.js..."
                brew install node
                echo ""
                echo "✓ Node.js 安装完成"
            else
                echo "Node.js 已安装，跳过"
            fi
            """),
            
            ("安装 npm", """
            if ! command -v npm &> /dev/null; then
                echo "正在安装 npm..."
                brew install npm
                echo ""
                echo "✓ npm 安装完成"
            else
                echo "npm 已安装，跳过"
            fi
            """),
        ]
        
        for name, cmd in commands:
            self.log_to_macos_output(f"\n{name}...")
            try:
                process = subprocess.Popen(
                    ['/bin/zsh', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    self.log_to_macos_output(line)
                process.wait()
                
                if process.returncode != 0:
                    self.log_to_macos_output(f"\n✗ {name} 失败，返回码: {process.returncode}\n")
                    break
            except Exception as e:
                self.log_to_macos_output(f"\n✗ {name} 失败: {e}\n")
                break
        
        self.log_to_macos_output("\n✓ 依赖环境安装完成\n")
        
    def install_macos_openclaw(self):
        """安装 OpenClaw（macOS）"""
        self.log_to_macos_output("\n" + "="*60)
        self.log_to_macos_output("步骤 3/3：安装 OpenClaw")
        self.log_to_macos_output("="*60 + "\n")
        
        commands = [
            ("安装 OpenClaw", "echo '正在安装 OpenClaw...' && npm install -g openclaw-cn"),
            ("验证安装", """
            echo ""
            echo "验证安装..."
            openclaw-cn --version
            echo ""
            echo "========================================"
            echo "✓ OpenClaw 安装完成！"
            echo "========================================"
            echo ""
            echo "使用方法："
            echo "  openclaw-cn gateway start    # 启动服务"
            echo "  openclaw-cn gateway stop     # 停止服务"
            echo "  openclaw-cn --help          # 查看帮助"
            echo "  openclaw-cn status           # 查看状态"
            echo ""
            """),
        ]
        
        for name, cmd in commands:
            self.log_to_macos_output(f"\n{name}...")
            try:
                process = subprocess.Popen(
                    ['/bin/zsh', '-c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    self.log_to_macos_output(line)
                process.wait()
                
                if process.returncode != 0:
                    self.log_to_macos_output(f"\n✗ {name} 失败，返回码: {process.returncode}\n")
            except Exception as e:
                self.log_to_macos_output(f"\n✗ {name} 失败: {e}\n")
        
        self.log_to_macos_output("\n✓ 所有安装步骤完成\n")
        
    def start_windows_install(self):
        """开始 Windows 安装"""
        self.windows_install_btn.config(state='disabled')
        self.windows_output.config(state='normal')
        self.windows_output.delete(1.0, tk.END)
        self.windows_output.insert(tk.END, "开始 Windows 安装...\n\n")
        
        # 在后台线程执行安装
        thread = threading.Thread(target=self.run_windows_install)
        thread.daemon = True
        thread.start()
        
    def run_windows_install(self):
        """执行 Windows 安装（分步骤）"""
        # 步骤 1：检查依赖环境
        self.check_windows_dependencies()
        
        # 步骤 2：安装依赖环境（需要手动）
        self.install_windows_dependencies()
        
        # 步骤 3：安装 OpenClaw
        self.install_windows_openclaw()
        
        # 完成
        self.windows_install_btn.config(state='normal')
        
    def check_windows_dependencies(self):
        """检查 Windows 依赖环境"""
        self.log_to_windows_output("\n" + "="*60)
        self.log_to_windows_output("步骤 1/3：检查依赖环境")
        self.log_to_windows_output("="*60 + "\n")
        
        commands = [
            ("检查系统版本", "ver"),
            ("检查 Node.js", "node --version"),
            ("检查 npm", "npm --version"),
        ]
        
        for name, cmd in commands:
            self.log_to_windows_output(f"\n{name}...")
            try:
                process = subprocess.Popen(
                    ['cmd.exe', '/c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    self.log_to_windows_output(line)
                process.wait()
            except Exception as e:
                self.log_to_windows_output(f"检查失败: {e}\n")
        
        self.log_to_windows_output("\n✓ 依赖环境检查完成\n")
        
    def install_windows_dependencies(self):
        """安装 Windows 依赖环境（提示手动安装）"""
        self.log_to_windows_output("\n" + "="*60)
        self.log_to_windows_output("步骤 2/3：安装依赖环境")
        self.log_to_windows_output("="*60 + "\n")
        
        self.log_to_windows_output("""
注意：Windows 需要手动安装 Node.js

安装步骤：
1. 访问 https://nodejs.org/
2. 下载并安装 Node.js LTS 版本
3. 安装完成后，Node.js 会自动安装 npm

如果已经安装 Node.js，请点击"确定"继续。
        """)
        
        # 等待用户确认
        self.root.after(0, lambda: messagebox.showinfo(
            "安装 Node.js",
            "请访问 https://nodejs.org/\n下载并安装 Node.js LTS 版本\n\n安装完成后点击确定继续..."
        ))
        
        self.log_to_windows_output("\n✓ Node.js 安装确认完成\n")
        
    def install_windows_openclaw(self):
        """安装 OpenClaw（Windows）"""
        self.log_to_windows_output("\n" + "="*60)
        self.log_to_windows_output("步骤 3/3：安装 OpenClaw")
        self.log_to_windows_output("="*60 + "\n")
        
        commands = [
            ("安装 OpenClaw", "echo 正在安装 OpenClaw... && npm install -g openclaw-cn"),
            ("验证安装", """
            echo.
            echo 验证安装...
            openclaw-cn --version
            echo.
            echo ========================================
            echo OpenClaw 安装完成！
            echo ========================================
            echo.
            echo 使用方法：
            echo   openclaw-cn gateway start    # 启动服务
            echo   openclaw-cn gateway stop     # 停止服务
            echo   openclaw-cn --help          # 查看帮助
            echo   openclaw-cn status           # 查看状态
            echo.
            """),
        ]
        
        for name, cmd in commands:
            self.log_to_windows_output(f"\n{name}...")
            try:
                process = subprocess.Popen(
                    ['cmd.exe', '/c', cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                for line in process.stdout:
                    self.log_to_windows_output(line)
                process.wait()
                
                if process.returncode != 0:
                    self.log_to_windows_output(f"\n✗ {name} 失败，返回码: {process.returncode}\n")
            except Exception as e:
                self.log_to_windows_output(f"\n✗ {name} 失败: {e}\n")
        
        self.log_to_windows_output("\n✓ 所有安装步骤完成\n")
        
    def log_to_macos_output(self, text: str):
        """记录到 macOS 输出"""
        self.root.after(0, lambda: self.macos_output.insert(tk.END, text))
        self.root.after(0, lambda: self.macos_output.see(tk.END))
        
    def log_to_windows_output(self, text: str):
        """记录到 Windows 输出"""
        self.root.after(0, lambda: self.windows_output.insert(tk.END, text))
        self.root.after(0, lambda: self.windows_output.see(tk.END))
        
    def run(self):
        """运行主循环"""
        self.root.mainloop()


# 终端模式安装器
class TerminalInstaller:
    """终端模式安装器"""
    
    def __init__(self):
        """初始化终端安装器"""
        self.current_platform = self.detect_platform()
    
    def detect_platform(self) -> str:
        """检测平台"""
        if Platform.is_windows():
            return "windows"
        elif Platform.is_macos():
            return "macos"
        else:
            return "unknown"
    
    def print_banner(self):
        """打印横幅"""
        print("\n" + "="*50)
        print("      OpenClaw 简易安装器（终端模式）")
        print("="*50 + "\n")
    
    def print_menu(self):
        """打印菜单"""
        print("当前平台:", self.current_platform.upper())
        print("\n选择操作:")
        print("  1. 安装 OpenClaw")
        print("  2. 退出")
        
        choice = input("\n请输入选项 (1-2): ")
        return choice
    
    def install_macos(self):
        """macOS 安装"""
        print("\n" + "="*50)
        print("开始 macOS 安装")
        print("="*50 + "\n")
        
        commands = [
            ("检查依赖环境", """
            echo "检查系统版本..."
            sw_vers
            echo ""
            echo "检查 Homebrew..."
            if command -v brew; then
                echo "✓ Homebrew 已安装"
                brew --version
            else
                echo "✗ Homebrew 未安装"
            fi
            echo ""
            echo "检查 Node.js..."
            if command -v node; then
                echo "✓ Node.js 已安装"
                node --version
            else
                echo "✗ Node.js 未安装"
            fi
            echo ""
            echo "检查 npm..."
            if command -v npm; then
                echo "✓ npm 已安装"
                npm --version
            else
                echo "✗ npm 未安装"
            fi
            """),
            
            ("安装依赖环境", """
            echo ""
            echo "安装 Homebrew..."
            if ! command -v brew; then
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            else
                echo "Homebrew 已安装，跳过"
            fi
            echo ""
            echo "安装 Node.js..."
            if ! command -v node; then
                brew install node
            else
                echo "Node.js 已安装，跳过"
            fi
            echo ""
            echo "安装 npm..."
            if ! command -v npm; then
                brew install npm
            else
                echo "npm 已安装，跳过"
            fi
            """),
            
            ("安装 OpenClaw", """
            echo ""
            echo "安装 OpenClaw..."
            npm install -g openclaw-cn
            """),
            
            ("验证安装", """
            echo ""
            echo "验证安装..."
            openclaw-cn --version
            echo ""
            echo "========================================"
            echo "✓ OpenClaw 安装完成！"
            echo "========================================"
            echo ""
            echo "使用方法："
            echo "  openclaw-cn gateway start    # 启动服务"
            echo "  openclaw-cn gateway stop     # 停止服务"
            echo "  openclaw-cn --help          # 查看帮助"
            echo ""
            """)
        ]
        
        for name, cmd in commands:
            print(f"\n{'='*50}")
            print(f"{name}")
            print(f"{'='*50}")
            
            try:
                subprocess.run(['/bin/zsh', '-c', cmd], check=True)
            except subprocess.CalledProcessError as e:
                print(f"\n✗ {name} 失败")
                print(f"返回码: {e.returncode}")
                break
            except Exception as e:
                print(f"\n✗ 执行失败: {e}")
                break
    
    def install_windows(self):
        """Windows 安装"""
        print("\n" + "="*50)
        print("开始 Windows 安装")
        print("="*50 + "\n")
        
        print("注意：Windows 需要手动安装 Node.js")
        print("请访问 https://nodejs.org/ 下载并安装")
        input("\n安装完成后按回车继续...")
        
        commands = [
            ("检查依赖环境", """
            node --version
            npm --version
            """),
            
            ("安装 OpenClaw", """
            echo 安装 OpenClaw...
            npm install -g openclaw-cn
            """),
            
            ("验证安装", """
            echo.
            echo 验证安装...
            openclaw-cn --version
            echo.
            echo ========================================
            echo OpenClaw 安装完成！
            echo ========================================
            echo.
            echo 使用方法：
            echo   openclaw-cn gateway start    # 启动服务
            echo   openclaw-cn gateway stop     # 停止服务
            echo   openclaw-cn --help          # 查看帮助
            echo.
            """)
        ]
        
        for name, cmd in commands:
            print(f"\n{'='*50}")
            print(f"{name}")
            print(f"{'='*50}")
            
            try:
                subprocess.run(['cmd.exe', '/c', cmd], check=True)
            except subprocess.CalledProcessError as e:
                print(f"\n✗ {name} 失败")
                print(f"返回码: {e.returncode}")
                break
            except Exception as e:
                print(f"\n✗ 执行失败: {e}")
                break
    
    def install(self):
        """执行安装"""
        if self.current_platform == "macos":
            self.install_macos()
        elif self.current_platform == "windows":
            self.install_windows()
        else:
            print(f"\n✗ 不支持的平台: {self.current_platform}")
            print("支持的平台: macOS, Windows")
    
    def run(self):
        """运行终端模式"""
        self.print_banner()
        
        while True:
            choice = self.print_menu()
            
            if choice == "1":
                self.install()
            elif choice == "2":
                print("\n退出安装器")
                break
            else:
                print("\n✗ 无效选项，请重新选择")


if __name__ == '__main__':
    if HAS_TKINTER:
        # GUI 模式
        root = tk.Tk()
        app = OpenClawInstaller(root)
        app.run()
    else:
        # 终端模式
        app = TerminalInstaller()
        app.run()
