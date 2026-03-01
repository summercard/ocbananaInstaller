#!/usr/bin/env python3
"""
OpenClaw 简易安装器 v2.2 - Windows 版
===============================
功能结构调整：
- 第一阶段：安装基础环境（Node.js + 环境变量刷新）
- 第二阶段：安装 OpenClaw 本体
- 第三阶段：静默配置 API Key
- 第四阶段：启动后台与对话

每个阶段都有执行过程和判断
"""

import subprocess
import threading
import sys
import os
import time

# 尝试导入 tkinter（GUI 模式）
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
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


class WindowsInstaller:
    """Windows 安装器 v2.2"""
    
    def __init__(self, root: tk.Tk = None):
        """初始化安装器"""
        self.root = root
        self.setup_window()
        self.create_ui()
        
    def setup_window(self):
        """设置窗口"""
        if self.root:
            self.root.title("OpenClaw 安装器 v2.2 - Windows")
            self.root.geometry("900x700")
            self.root.minsize(700, 500)
            self.center_window()
        
    def center_window(self):
        """窗口居中"""
        if self.root:
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
        if not self.root:
            return
            
        # 主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(
            main_frame,
            text="OpenClaw 安装器 v2.2",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 副标题
        subtitle_label = ttk.Label(
            main_frame,
            text="Windows 版 - 分阶段安装",
            font=('Helvetica', 10)
        )
        subtitle_label.pack(pady=(0, 15))
        
        # 安装阶段按钮框架
        self.stages_frame = ttk.LabelFrame(main_frame, text="安装阶段")
        self.stages_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 四个阶段的按钮
        btn_frame = ttk.Frame(self.stages_frame)
        btn_frame.pack(padx=10, pady=10)
        
        # 第一阶段按钮
        self.stage1_btn = ttk.Button(
            btn_frame,
            text="第一阶段\n安装基础环境",
            command=self.start_stage1,
            width=18
        )
        self.stage1_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # 第二阶段按钮
        self.stage2_btn = ttk.Button(
            btn_frame,
            text="第二阶段\n安装 OpenClaw 本体",
            command=self.start_stage2,
            width=18,
            state='disabled'
        )
        self.stage2_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # 第三阶段按钮
        self.stage3_btn = ttk.Button(
            btn_frame,
            text="第三阶段\n配置 API Key",
            command=self.start_stage3,
            width=18,
            state='disabled'
        )
        self.stage3_btn.grid(row=1, column=0, padx=5, pady=5)
        
        # 第四阶段按钮
        self.stage4_btn = ttk.Button(
            btn_frame,
            text="第四阶段\n启动与对话",
            command=self.start_stage4,
            width=18,
            state='disabled'
        )
        self.stage4_btn.grid(row=1, column=1, padx=5, pady=5)
        
        # 当前状态显示
        self.status_label = ttk.Label(
            main_frame,
            text="当前状态：等待开始",
            font=('Helvetica', 10)
        )
        self.status_label.pack(pady=(0, 5))
        
        # 进度条
        self.progress = ttk.Progressbar(
            main_frame,
            mode='determinate',
            length=300
        )
        self.progress.pack(pady=(0, 10))
        
        # 终端输出
        terminal_frame = ttk.LabelFrame(main_frame, text="执行输出")
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.output_text = scrolledtext.ScrolledText(
            terminal_frame,
            height=20,
            wrap=tk.WORD,
            state='disabled',
            font=('Consolas', 9)
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 底部说明
        info_frame = ttk.LabelFrame(main_frame, text="操作说明")
        info_frame.pack(fill=tk.X)
        
        info_text = """
        安装顺序：按阶段顺序执行（1 → 2 → 3 → 4）
        每个阶段执行后会有判断，通过后才能进行下一阶段
        如需重新开始，请关闭程序后重新启动
        """
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(padx=10, pady=5)
        
    # ==================== 输出日志相关 ====================
    
    def log_output(self, text: str):
        """输出日志到界面"""
        if self.root:
            self.root.after(0, lambda: self._do_log(text))
    
    def _do_log(self, text: str):
        """实际执行日志写入"""
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')
    
    def clear_output(self):
        """清空输出"""
        if self.root:
            self.output_text.config(state='normal')
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state='disabled')
    
    def update_status(self, text: str):
        """更新状态"""
        if self.root:
            self.root.after(0, lambda: self.status_label.config(text=text))
    
    def update_progress(self, value: float):
        """更新进度条"""
        if self.root:
            self.root.after(0, lambda: self.progress.config(value=value))
    
    # ==================== 命令执行相关 ====================
    
    def run_command(self, cmd: str, shell: bool = True) -> tuple:
        """执行命令并返回 (returncode, stdout, stderr)"""
        self.log_output(f"\n$ {cmd}\n")
        self.log_output("-" * 50 + "\n")
        
        try:
            if shell:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            else:
                process = subprocess.Popen(
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
            
            output_lines = []
            for line in process.stdout:
                self.log_output(line)
                output_lines.append(line)
            
            process.wait()
            output = "".join(output_lines)
            
            self.log_output("-" * 50 + "\n")
            self.log_output(f"返回码: {process.returncode}\n\n")
            
            return process.returncode, output, ""
            
        except Exception as e:
            self.log_output(f"✗ 执行失败: {e}\n")
            return -1, "", str(e)
    
    def check_command(self, cmd: str) -> bool:
        """检查命令是否成功执行"""
        returncode, stdout, stderr = self.run_command(cmd)
        return returncode == 0
    
    # ==================== 第一阶段：安装基础环境 ====================
    
    def start_stage1(self):
        """开始第一阶段安装"""
        self.clear_output()
        self.update_status("第一阶段：安装基础环境")
        self.update_progress(10)
        self.stage1_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.run_stage1)
        thread.daemon = True
        thread.start()
    
    def run_stage1(self):
        """执行第一阶段安装"""
        self.log_output("=" * 60 + "\n")
        self.log_output("第一阶段：安装基础环境")
        self.log_output("=" * 60 + "\n\n")
        
        # 1. 使用 winget 静默安装 Node.js LTS 版本
        self.log_output("【步骤 1/2】使用 winget 安装 Node.js LTS\n")
        self.log_output("执行命令: winget install OpenJS.NodeJS.LTS\n")
        
        returncode, stdout, stderr = self.run_command(
            'winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements'
        )
        
        if returncode == 0:
            self.log_output("✓ Node.js 安装命令已执行\n")
        else:
            self.log_output("✗ Node.js 安装失败，可能需要手动安装\n")
            self.log_output("请访问 https://nodejs.org/ 下载并安装\n")
        
        # 2. 刷新环境变量（手动操作）- 需要提醒
        self.log_output("\n【步骤 2/2】刷新环境变量\n")
        self.log_output("=" * 60 + "\n")
        self.log_output("⚠️  重要提示：安装完成后，请执行以下操作：\n\n")
        self.log_output("1. 关闭当前 CMD 窗口\n")
        self.log_output("2. 重新以管理员身份打开一个新的 CMD 窗口\n")
        self.log_output("3. 在新窗口中验证 Node.js 安装：node --version\n\n")
        
        # 弹窗提醒
        if self.root:
            self.root.after(0, lambda: messagebox.showinfo(
                "环境变量刷新",
                "请关闭当前 CMD 窗口，\n然后重新以管理员身份打开一个新的 CMD 窗口，\n然后点击确定继续..."
            ))
        
        # 检查 Node.js 是否可用
        self.log_output("\n检查 Node.js 安装状态...\n")
        returncode, stdout, stderr = self.run_command('node --version')
        
        if returncode == 0 and "v" in stdout:
            self.log_output("✓ Node.js 已安装并生效\n")
            self.stage2_btn.config(state='normal')
            self.update_status("第一阶段完成 - 可进入第二阶段")
            self.update_progress(25)
        else:
            self.log_output("✗ Node.js 尚未生效\n")
            self.log_output("请确保已关闭并重新打开 CMD 窗口\n")
            self.stage1_btn.config(state='normal')
            self.update_status("等待环境变量刷新")
    
    # ==================== 第二阶段：安装 OpenClaw 本体 ====================
    
    def start_stage2(self):
        """开始第二阶段安装"""
        self.update_status("第二阶段：安装 OpenClaw 本体")
        self.update_progress(40)
        self.stage2_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.run_stage2)
        thread.daemon = True
        thread.start()
    
    def run_stage2(self):
        """执行第二阶段安装"""
        self.log_output("=" * 60 + "\n")
        self.log_output("第二阶段：安装 OpenClaw 本体")
        self.log_output("=" * 60 + "\n\n")
        
        # 1. 检查环境版本
        self.log_output("【步骤 1/2】检查环境版本\n")
        
        returncode, stdout, stderr = self.run_command('node --version')
        
        if returncode == 0:
            version = stdout.strip()
            self.log_output(f"Node.js 版本: {version}\n")
            
            # 检查是否为 v22 或以上
            try:
                major_version = int(version.replace("v", "").split(".")[0])
                if major_version >= 22:
                    self.log_output("✓ Node.js 版本符合要求 (v22+)\n")
                else:
                    self.log_output(f"✗ Node.js 版本过低，需要 v22 或更高\n")
                    self.stage2_btn.config(state='normal')
                    self.update_status("Node.js 版本过低")
                    return
            except:
                self.log_output("⚠️  无法解析版本号，继续尝试安装\n")
        else:
            self.log_output("✗ Node.js 不可用，请先完成第一阶段\n")
            self.stage2_btn.config(state='normal')
            return
        
        # 2. 全局安装 OpenClaw
        self.log_output("\n【步骤 2/2】全局安装 OpenClaw\n")
        
        returncode, stdout, stderr = self.run_command('npm install -g openclaw-cn')
        
        if returncode == 0:
            self.log_output("✓ OpenClaw 安装成功\n")
            self.stage3_btn.config(state='normal')
            self.update_status("第二阶段完成 - 可进入第三阶段")
            self.update_progress(55)
        else:
            self.log_output("✗ OpenClaw 安装失败\n")
            self.stage2_btn.config(state='normal')
            self.update_status("安装失败，请重试")
    
    # ==================== 第三阶段：静默配置 API Key ====================
    
    def start_stage3(self):
        """开始第三阶段配置"""
        self.update_status("第三阶段：配置 API Key")
        self.update_progress(70)
        
        # 弹出对话框获取 API Key
        if self.root:
            dialog = APIKeyDialog(self.root)
            self.root.wait_window(dialog.dialog)
            
            if dialog.api_key:
                self.api_key = dialog.api_key
                thread = threading.Thread(target=self.run_stage3)
                thread.daemon = True
                thread.start()
            else:
                self.update_status("等待输入 API Key")
        else:
            # 终端模式
            self.api_key = input("请输入 API Key: ").strip()
            if self.api_key:
                thread = threading.Thread(target=self.run_stage3)
                thread.daemon = True
                thread.start()
    
    def run_stage3(self):
        """执行第三阶段配置"""
        self.log_output("=" * 60 + "\n")
        self.log_output("第三阶段：静默配置 API Key")
        self.log_output("=" * 60 + "\n\n")
        
        api_key = self.api_key
        
        # 1. 创建配置文件夹
        self.log_output("【步骤 1/4】创建配置文件夹\n")
        
        config_dir = os.path.join(os.environ.get('APPDATA', ''), 'openclaw')
        self.log_output(f"配置目录: {config_dir}\n")
        
        try:
            os.makedirs(config_dir, exist_ok=True)
            self.log_output("✓ 配置文件夹已创建\n")
        except Exception as e:
            self.log_output(f"✗ 创建失败: {e}\n")
            return
        
        # 2. 写入 API 密钥
        self.log_output("\n【步骤 2/4】写入 API 密钥\n")
        
        config_file = os.path.join(config_dir, 'config.yaml')
        
        # 读取现有配置或创建新配置
        config_content = ""
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_content = f.read()
            except:
                pass
        
        # 添加 API Key 配置
        if 'apiKeys:' not in config_content:
            config_content += "\napiKeys:\n  anthropic: " + api_key + "\n"
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            self.log_output("✓ API 密钥已写入配置文件\n")
        except Exception as e:
            self.log_output(f"✗ 写入失败: {e}\n")
            return
        
        # 3. 启用服务商
        self.log_output("\n【步骤 3/4】启用服务商\n")
        
        returncode, stdout, stderr = self.run_command(
            f'openclaw-cn config set providers.anthropic.enabled true'
        )
        
        if returncode == 0:
            self.log_output("✓ Anthropic 服务商已启用\n")
        else:
            self.log_output("⚠️  手动启用服务商\n")
        
        # 4. 设置默认模型
        self.log_output("\n【步骤 4/4】设置默认模型\n")
        
        returncode, stdout, stderr = self.run_command(
            'openclaw-cn config set defaultModel claude-sonnet-4-20250514'
        )
        
        if returncode == 0:
            self.log_output("✓ 默认模型已设置\n")
        else:
            self.log_output("⚠️  手动设置默认模型\n")
        
        self.log_output("\n✓ API Key 配置完成\n")
        self.stage4_btn.config(state='normal')
        self.update_status("第三阶段完成 - 可进入第四阶段")
        self.update_progress(85)
    
    # ==================== 第四阶段：启动后台与对话 ====================
    
    def start_stage4(self):
        """开始第四阶段启动"""
        self.update_status("第四阶段：启动与对话")
        self.stage4_btn.config(state='disabled')
        
        thread = threading.Thread(target=self.run_stage4)
        thread.daemon = True
        thread.start()
    
    def run_stage4(self):
        """执行第四阶段启动"""
        self.log_output("=" * 60 + "\n")
        self.log_output("第四阶段：启动后台与对话")
        self.log_output("=" * 60 + "\n\n")
        
        # 1. 安装守护进程
        self.log_output("【步骤 1/3】安装守护进程\n")
        
        returncode, stdout, stderr = self.run_command(
            'openclaw-cn gateway install'
        )
        
        if returncode == 0:
            self.log_output("✓ 守护进程已安装\n")
        else:
            self.log_output("⚠️  守护进程安装失败，继续尝试启动\n")
        
        # 2. 启动网关
        self.log_output("\n【步骤 2/3】启动网关\n")
        
        returncode, stdout, stderr = self.run_command(
            'openclaw-cn gateway start'
        )
        
        if returncode == 0:
            self.log_output("✓ 网关已启动\n")
        else:
            self.log_output("⚠️  网关启动失败\n")
        
        # 等待一下让服务启动
        self.log_output("\n等待服务启动...\n")
        time.sleep(2)
        
        # 3. 进入对话终端
        self.log_output("\n【步骤 3/3】进入对话终端\n")
        
        self.log_output("\n" + "=" * 60 + "\n")
        self.log_output("✓ 安装全部完成！\n")
        self.log_output("=" * 60 + "\n\n")
        
        self.log_output("使用方法：\n")
        self.log_output("  openclaw-cn gateway start    # 启动服务\n")
        self.log_output("  openclaw-cn gateway stop     # 停止服务\n")
        self.log_output("  openclaw-cn --help          # 查看帮助\n")
        self.log_output("  openclaw-cn status           # 查看状态\n")
        
        self.update_status("全部安装完成！")
        self.update_progress(100)
        
        # 弹窗提示
        if self.root:
            self.root.after(0, lambda: messagebox.showinfo(
                "安装完成",
                "OpenClaw 安装完成！\n\n"
                "使用命令启动对话：\n"
                "openclaw-cn"
            ))
    
    def run(self):
        """运行主循环"""
        if self.root:
            self.root.mainloop()


class APIKeyDialog:
    """API Key 输入对话框"""
    
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("输入 API Key")
        self.dialog.geometry("500x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.api_key = None
        
        # 居中
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 500) // 2
        y = (self.dialog.winfo_screenheight() - 200) // 2
        self.dialog.geometry(f"500x200+{x}+{y}")
        
        # 说明
        info_label = ttk.Label(
            self.dialog,
            text="请输入 Anthropic Claude API Key",
            font=('Helvetica', 11)
        )
        info_label.pack(pady=(20, 10))
        
        info_label2 = ttk.Label(
            self.dialog,
            text="（可在 anthropic.com 获取）",
            font=('Helvetica', 9)
        )
        info_label2.pack(pady=(0, 10))
        
        # 输入框
        self.entry = ttk.Entry(self.dialog, width=50, show="*")
        self.entry.pack(pady=10)
        
        # 按钮
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=20)
        
        ttk.Button(
            btn_frame,
            text="确认",
            command=self.on_ok
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="取消",
            command=self.on_cancel
        ).pack(side=tk.LEFT, padx=5)
        
        self.entry.focus()
        self.entry.bind('<Return>', lambda e: self.on_ok())
        
    def on_ok(self):
        self.api_key = self.entry.get().strip()
        if self.api_key:
            self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请输入 API Key")
    
    def on_cancel(self):
        self.api_key = None
        self.dialog.destroy()


# 终端模式安装器
class TerminalInstaller:
    """终端模式安装器"""
    
    def __init__(self):
        """初始化终端安装器"""
        self.api_key = ""
        self.platform = self.detect_platform()
    
    def detect_platform(self) -> str:
        """检测平台"""
        if Platform.is_windows():
            return "windows"
        elif Platform.is_macos():
            return "macos"
        else:
            return "unknown"
    
    def run_command(self, cmd: str, shell: bool = True) -> tuple:
        """执行命令并返回 (returncode, stdout, stderr)"""
        print(f"\n$ {cmd}")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                cmd if shell else cmd.split(),
                shell=shell,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr)
            
            print(f"返回码: {result.returncode}")
            return result.returncode, result.stdout, result.stderr
            
        except Exception as e:
            print(f"✗ 执行失败: {e}")
            return -1, "", str(e)
    
    def print_banner(self):
        """打印横幅"""
        print("\n" + "=" * 50)
        print("   OpenClaw 简易安装器 v2.2（终端模式）")
        print("=" * 50 + "\n")
    
    def run(self):
        """运行终端模式"""
        self.print_banner()
        
        if self.platform != "windows":
            print(f"⚠️  此版本仅支持 Windows，检测到平台: {self.platform}")
            return
        
        print("Windows 安装流程\n")
        
        # 第一阶段
        print("=" * 50)
        print("第一阶段：安装基础环境")
        print("=" * 50)
        
        print("\n使用 winget 安装 Node.js LTS...")
        self.run_command('winget install OpenJS.NodeJS.LTS --silent --accept-package-agreements --accept-source-agreements')
        
        print("\n⚠️  请关闭当前 CMD 窗口，重新以管理员身份打开新窗口")
        input("然后按回车继续...")
        
        # 检查 Node.js
        returncode, stdout, stderr = self.run_command('node --version')
        if returncode != 0:
            print("✗ Node.js 未安装或未生效")
            return
        
        print(f"✓ Node.js 版本: {stdout.strip()}")
        
        # 第二阶段
        print("\n" + "=" * 50)
        print("第二阶段：安装 OpenClaw 本体")
        print("=" * 50)
        
        self.run_command('npm install -g openclaw-cn')
        
        # 第三阶段
        print("\n" + "=" * 50)
        print("第三阶段：配置 API Key")
        print("=" * 50)
        
        self.api_key = input("请输入 Anthropic Claude API Key: ").strip()
        
        if self.api_key:
            config_dir = os.path.join(os.environ.get('APPDATA', ''), 'openclaw')
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = os.path.join(config_dir, 'config.yaml')
            config_content = f"apiKeys:\n  anthropic: {self.api_key}\n"
            
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            print("✓ API Key 已配置")
        
        # 第四阶段
        print("\n" + "=" * 50)
        print("第四阶段：启动后台与对话")
        print("=" * 50)
        
        self.run_command('openclaw-cn gateway install')
        self.run_command('openclaw-cn gateway start')
        
        print("\n" + "=" * 50)
        print("✓ 安装完成！")
        print("=" * 50)
        print("\n使用命令启动对话: openclaw-cn")


if __name__ == '__main__':
    if HAS_TKINTER:
        # GUI 模式
        root = tk.Tk()
        app = WindowsInstaller(root)
        app.run()
    else:
        # 终端模式
        app = TerminalInstaller()
        app.run()
