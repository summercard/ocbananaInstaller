#!/usr/bin/env python3
"""
OpenClaw 傻瓜安装与配置器
- 增加 Mac / Win 系统切换开关
- 第一层：安装系统依赖、安装 OpenClaw、打开 OpenClaw
- 第二层：启停控制、配置 API 等
- 核心逻辑：前端为 GUI，所有操作均拼接为针对特定系统的终端命令，发送至后台执行并实时回显日志
"""

import subprocess
import threading
import sys
import os
import json

# 尝试导入 tkinter
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False
    print("⚠️  Tkinter 未安装，请安装 Python 的 tkinter 模块")

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  Pillow 未安装，如需显示侧边图片，请安装 Pillow 模块 (pip install pillow)")

# OpenClaw 标准配置模板 (基于原生 openclaw.json 结构)
OPENCLAW_CONFIG_TEMPLATE = '''
{
  "meta": {
    "lastTouchedVersion": "2026.2.25",
    "lastTouchedAt": "2026-02-28T00:00:00.000Z"
  },
  "env": {
    "MINIMAX_API_KEY": "{{MINIMAX_API_KEY}}",
    "OPENAI_API_KEY": "{{OPENAI_API_KEY}}"
  },
  "models": {
    "mode": "merge",
    "providers": {
      "minimax": {
        "baseUrl": "https://api.minimax.chat/v1",
        "apiKey": "${MINIMAX_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "MiniMax-M2.1",
            "name": "MiniMax M2.1",
            "reasoning": false,
            "input": ["text"],
            "contextWindow": 200000,
            "maxTokens": 8192
          }
        ]
      },
      "openai": {
        "baseUrl": "https://api.openai.com/v1",
        "apiKey": "${OPENAI_API_KEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "gpt-4o",
            "name": "GPT-4o",
            "reasoning": false,
            "input": ["text", "image"],
            "contextWindow": 128000,
            "maxTokens": 4096
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "{{DEFAULT_MODEL}}"
      },
      "models": {
        "minimax/MiniMax-M2.1": {},
        "openai/gpt-4o": {}
      },
      "workspace": "{{WORKSPACE_PATH}}",
      "compaction": {
        "mode": "safeguard"
      }
    }
  },
  "commands": {
    "native": "auto",
    "nativeSkills": "auto",
    "restart": true,
    "ownerDisplay": "raw"
  },
  "gateway": {
    "mode": "local",
    "port": {{GATEWAY_PORT}},
    "auth": {
      "mode": "token",
      "token": "{{GATEWAY_TOKEN}}"
    }
  },
  "plugins": {
    "entries": {}
  }
}
'''

# 平台检测
import platform
class Platform:
    @staticmethod
    def is_windows():
        return platform.system() == 'Windows'
    @staticmethod
    def is_macos():
        return platform.system() == 'Darwin'

def get_asset_path(relative_path):
    """获取资源文件的绝对路径（兼容 PyInstaller 打包环境）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时目录
        base_path = sys._MEIPASS
    else:
        # 开发环境目录
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class OpenClawApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("OpenClaw 安装与配置台")
        self.root.geometry("850x850")
        self.root.minsize(900, 750)
        self.center_window()
        
        # 尝试设置窗口图标
        self.set_window_icon()
        
        # 配置文件路径 (修复为原生 OpenClaw 默认路径)
        self.config_dir = os.path.join(os.path.expanduser("~"), ".openclaw")
        self.config_file = os.path.join(self.config_dir, "openclaw.json")
        
        # 固定使用的 Gateway Token
        self.gateway_token = "8ab524d343c8b93b99b3a0c5babcf4ab108a1b3cccb03fef"
        
        self.create_ui()
        self.load_config()

    def center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def set_window_icon(self):
        """尝试设置窗口左上角的软件图标"""
        icon_path = get_asset_path(os.path.join('image', 'icon.png'))
        if os.path.exists(icon_path):
            try:
                # Tkinter 的 iconphoto 需要 PhotoImage 格式
                img = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(True, img)
            except Exception as e:
                print(f"⚠️  设置图标失败: {e}")

    def create_ui(self):
        # 整体分左右两栏结构：左边是图片侧边栏，右边是原本的主工作区
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # ====== 左侧：图片区域 ======
        self.left_sidebar = tk.Frame(self.main_container, width=280, bg="#2a2a2a")
        self.left_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.left_sidebar.pack_propagate(False) # 强制保持固定宽度
        
        self.load_sidebar_image()
        
        # ====== 右侧：原本的业务区域 ======
        self.right_workspace = ttk.Frame(self.main_container)
        self.right_workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 顶部：环境与网络设置 (放在右侧工作区)
        env_frame = ttk.LabelFrame(self.right_workspace, text="环境与网络设置 (命令将据此生成)")
        env_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # 默认选中当前真实系统
        default_os = "windows" if Platform.is_windows() else "macos"
        self.os_var = tk.StringVar(value=default_os)
        
        ttk.Radiobutton(env_frame, text="Windows 系统", variable=self.os_var, value="windows").pack(side=tk.LEFT, padx=15, pady=5)
        ttk.Radiobutton(env_frame, text="macOS / Linux 系统", variable=self.os_var, value="macos").pack(side=tk.LEFT, padx=15, pady=5)

        # 镜像加速选择
        self.use_mirror_var = tk.BooleanVar(value=True)  # 默认勾选国内镜像
        ttk.Checkbutton(env_frame, text="使用国内镜像加速 (推荐)", variable=self.use_mirror_var).pack(side=tk.RIGHT, padx=20, pady=5)

        # 视图区域 (通过 tk.Frame 切换 Layer 1 和 Layer 2)
        self.view_container = ttk.Frame(self.right_workspace)
        self.view_container.pack(fill=tk.X, padx=10, pady=10)
        
        self.layer1_frame = ttk.Frame(self.view_container)
        self.layer2_frame = ttk.Frame(self.view_container)
        
        self.build_layer1()
        self.build_layer2()
        
        # 默认显示 Layer 1
        self.show_layer1()
        
        # 底部：终端输出区域
        terminal_frame = ttk.LabelFrame(self.right_workspace, text="终端输出 (后台执行日志)")
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame, wrap=tk.NONE, font=('Consolas', 10), bg="#1e1e1e", fg="#00ff00"
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        h_scroll = ttk.Scrollbar(self.terminal_output, orient=tk.HORIZONTAL, command=self.terminal_output.xview)
        self.terminal_output['xscrollcommand'] = h_scroll.set

    def load_sidebar_image(self):
        """加载左侧侧边栏的美化图片 002.png"""
        img_path = get_asset_path(os.path.join('image', '002.png'))
        if not os.path.exists(img_path):
            # 图片不存在，显示一个占位文本
            placeholder = tk.Label(self.left_sidebar, text="OpenClaw\nImage not found", fg="white", bg="#2a2a2a", font=('Helvetica', 14))
            placeholder.pack(expand=True)
            return
            
        if HAS_PIL:
            try:
                # 使用 Pillow 加载并等比例缩放图片以适应侧边栏高度
                pil_img = Image.open(img_path)
                
                # 调整图片大小策略：保持比例，宽度填满 280，或者高度自适应
                # 在窗口大小改变时动态缩放比较复杂，这里我们先缩放一个适合初始高度(约750)的固定大小
                target_w = 280
                w_percent = (target_w / float(pil_img.size[0]))
                target_h = int((float(pil_img.size[1]) * float(w_percent)))
                
                # 如果图片缩放后高度大于窗口初始高度，可以裁剪或者进一步缩小。
                # 由于这是立绘角色图，我们这里仅等宽缩放。如果下面超出了会被 Frame 切掉。
                pil_img = pil_img.resize((target_w, target_h), Image.LANCZOS)
                
                self.sidebar_photo = ImageTk.PhotoImage(pil_img)
                lbl = tk.Label(self.left_sidebar, image=self.sidebar_photo, bg="#2a2a2a")
                lbl.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                print(f"⚠️  加载侧边栏图片失败: {e}")
        else:
            try:
                # 没有 PIL，只能尝试用 tk.PhotoImage 直接加载 (仅支持 PNG/GIF, 不支持缩放)
                self.sidebar_photo = tk.PhotoImage(file=img_path)
                lbl = tk.Label(self.left_sidebar, image=self.sidebar_photo, bg="#2a2a2a")
                lbl.pack(fill=tk.BOTH, expand=True)
            except Exception as e:
                print(f"⚠️  基础组件加载图片失败: {e}")

    def build_layer1(self):
        """构建第一层：安装界面"""
        lbl = ttk.Label(self.layer1_frame, text="OpenClaw 傻瓜安装器", font=('Helvetica', 18, 'bold'))
        lbl.pack(pady=10)
        
        desc = ttk.Label(self.layer1_frame, text="为了保证稳定，请按顺序分别检查和安装：", font=('Helvetica', 12))
        desc.pack(pady=5)
        
        btn_frame = ttk.Frame(self.layer1_frame)
        btn_frame.pack(pady=5)
        
        btn_style = {'ipadx': 10, 'ipady': 5, 'pady': 3, 'fill': tk.X}
        
        btn0 = ttk.Button(btn_frame, text="1. 检查环境 (查看是否已安装 Node.js 和 Git)", command=self.cmd_check_deps)
        btn0.pack(**btn_style)

        btn1 = ttk.Button(btn_frame, text="2. 安装 Node.js (若步骤1提示缺失则点击)", command=self.cmd_install_node)
        btn1.pack(**btn_style)
        
        btn2 = ttk.Button(btn_frame, text="3. 安装 Git (若步骤1提示缺失则点击)", command=self.cmd_install_git)
        btn2.pack(**btn_style)
        
        btn3 = ttk.Button(btn_frame, text="4. 安装 OpenClaw 核心", command=self.cmd_install_openclaw)
        btn3.pack(**btn_style)
        
        btn4 = ttk.Button(btn_frame, text="5. 测试安装 (查看 OpenClaw 版本)", command=self.cmd_test_openclaw)
        btn4.pack(**btn_style)
        
        btn5 = ttk.Button(btn_frame, text="6. 注册后台网关服务 (Gateway Install)", command=self.cmd_install_gateway)
        btn5.pack(**btn_style)
        
        btn6 = ttk.Button(btn_frame, text="7. 进入控制台 (服务启停与配置) ➔", command=self.show_layer2)
        btn6.pack(ipadx=10, ipady=8, pady=8, fill=tk.X)

    def build_layer2(self):
        """构建第二层：控制与配置界面"""
        # 顶部导航
        nav_frame = ttk.Frame(self.layer2_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        back_btn = ttk.Button(nav_frame, text="← 返回安装界面", command=self.show_layer1)
        back_btn.pack(side=tk.LEFT)
        
        lbl = ttk.Label(nav_frame, text="OpenClaw 控制台", font=('Helvetica', 16, 'bold'))
        lbl.pack(side=tk.LEFT, padx=20)
        
        # 左右分栏：左侧服务控制，右侧API配置
        content_frame = ttk.Frame(self.layer2_frame)
        content_frame.pack(fill=tk.X, pady=10)
        
        # 左侧：服务控制
        ctrl_frame = ttk.LabelFrame(content_frame, text="服务控制")
        ctrl_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 状态指示灯区域
        status_frame = ttk.Frame(ctrl_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(status_frame, text="当前服务状态:", font=('Helvetica', 10, 'bold')).pack(side=tk.LEFT)
        self.status_indicator = ttk.Label(status_frame, text="⚫ 未知", font=('Helvetica', 10, 'bold'), foreground="gray")
        self.status_indicator.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(ctrl_frame, text="▶ 启动服务 (Gateway Start)", command=self.cmd_start_service).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(ctrl_frame, text="■ 停止服务 (Gateway Stop)", command=self.cmd_stop_service).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(ctrl_frame, text="ℹ 查看状态 (刷新指示灯)", command=self.cmd_check_status).pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(ctrl_frame, text="🌐 打开 Web UI (浏览器)", command=self.cmd_open_webui).pack(fill=tk.X, padx=10, pady=5)

        # 右侧：API 配置
        cfg_frame = ttk.LabelFrame(content_frame, text="API 配置 (原生 openclaw.json)")
        cfg_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 表单字段
        self.cfg_vars = {
            'api_type': tk.StringVar(value='minimax'),
            'api_url': tk.StringVar(value='https://api.minimax.chat/v1'),
            'api_key': tk.StringVar(),
            'model_name': tk.StringVar(value='MiniMax-M2.1'),
            'port': tk.StringVar(value='18789')
        }
        
        fields = [
            ("API 服务商:", 'api_type'),
            ("API URL:", 'api_url'),
            ("API Key:", 'api_key'),
            ("模型名称:", 'model_name'),
            ("服务端口:", 'port')
        ]
        
        for idx, (label_text, var_name) in enumerate(fields):
            f = ttk.Frame(cfg_frame)
            f.pack(fill=tk.X, padx=10, pady=3)
            ttk.Label(f, text=label_text, width=12).pack(side=tk.LEFT)
            if var_name == 'api_type':
                cb = ttk.Combobox(f, textvariable=self.cfg_vars[var_name], values=['minimax', 'openai', 'custom'])
                cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif var_name == 'api_key':
                ttk.Entry(f, textvariable=self.cfg_vars[var_name], show="*").pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                ttk.Entry(f, textvariable=self.cfg_vars[var_name]).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        ttk.Button(cfg_frame, text="💾 保存并应用配置", command=self.cmd_save_config).pack(pady=10)

    def show_layer1(self):
        self.layer2_frame.pack_forget()
        self.layer1_frame.pack(fill=tk.BOTH, expand=True)

    def show_layer2(self):
        self.layer1_frame.pack_forget()
        self.layer2_frame.pack(fill=tk.BOTH, expand=True)

    # =================终端命令执行核心=================
    def log_terminal(self, text):
        self.root.after(0, lambda: self.terminal_output.insert(tk.END, text))
        self.root.after(0, lambda: self.terminal_output.see(tk.END))

    def run_command_in_bg(self, cmd_desc, command):
        """后台运行终端命令并实时输出"""
        current_os = self.os_var.get()
        self.log_terminal(f"\n[{cmd_desc}] 目标系统: {current_os.upper()} | 执行命令:\n> {command}\n{'-'*60}\n")
        
        def task():
            try:
                # 根据当前选择的 OS 切换 Shell 执行器
                if current_os == "windows":
                    creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                    # 去掉 text=True，改用二进制读取以手动处理编码错误
                    process = subprocess.Popen(['cmd.exe', '/c', command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=creationflags)
                else:
                    process = subprocess.Popen(['/bin/sh', '-c', command], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                
                for line in process.stdout:
                    # 手动解码，并忽略乱码错误
                    if current_os == "windows":
                        decoded_line = line.decode('gbk', errors='replace')
                    else:
                        decoded_line = line.decode('utf-8', errors='replace')
                    
                    self.log_terminal(decoded_line)
                    
                    # 状态指示灯监控逻辑 (简易版)
                    if "status" in command.lower() and hasattr(self, 'status_indicator'):
                        lower_line = decoded_line.lower()
                        if "gateway service missing" in lower_line or "missing" in lower_line and "scheduled task" in lower_line:
                            self.root.after(0, lambda: self.status_indicator.config(text="🔴 服务未安装/缺失", foreground="red"))
                        elif "stopped" in lower_line or "not running" in lower_line:
                            self.root.after(0, lambda: self.status_indicator.config(text="🟡 已停止", foreground="orange"))
                        elif "running" in lower_line and "pid" in lower_line or "started" in lower_line:
                            self.root.after(0, lambda: self.status_indicator.config(text="🟢 运行中", foreground="green"))
                
                process.wait()
                self.log_terminal(f"\n[执行完成] 返回码: {process.returncode}\n{'='*60}\n")
                
                # 如果刚才成功执行了 winget 安装 node 或 git，弹出重点提示
                if current_os == "windows" and "winget install" in command and process.returncode == 0:
                    msg = "\n👉 【重要提示】: 系统依赖刚安装完毕！\n请**先关闭本安装器，然后再重新打开**，让系统重新加载环境变量。然后再进行下一步操作，否则系统会提示找不到命令！\n"
                    self.log_terminal(msg)
                    messagebox.showinfo("重启提示", "环境依赖安装成功！\n请关闭本软件并重新打开，以刷新环境变量，然后再进行下一步。")
                    
            except Exception as e:
                self.log_terminal(f"\n[执行错误]: {str(e)}\n{'='*60}\n")

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

    # ================= Layer 1 功能 (按系统区分命令) =================
    
    def cmd_check_deps(self):
        """仅检查依赖，不自动安装"""
        target_os = self.os_var.get()
        if target_os == "macos":
            cmd = """
            echo "==== 检查 macOS 依赖环境 ===="
            echo "1. 检查 Homebrew:"
            brew --version || echo "❌ 未安装 Homebrew"
            echo "-------------------"
            echo "2. 检查 Node.js:"
            node -v || echo "❌ 未安装 Node.js"
            echo "-------------------"
            echo "3. 检查 Git:"
            git --version || echo "❌ 未安装 Git"
            echo "==== 检查完毕 ===="
            """
        else:
            # Windows 纯检查，将多行命令通过 && 串联，或者直接写成单行多语句
            cmd = "echo ==== 检查 Windows 依赖环境 ==== & echo 1. 检查 Node.js: & node -v || echo [X] 未安装 Node.js & echo ------------------- & echo 2. 检查 Git: & git --version || echo [X] 未安装 Git & echo ==== 检查完毕 ===="
        self.run_command_in_bg("环境检查", cmd)

    def cmd_install_node(self):
        """单独安装 Node.js"""
        target_os = self.os_var.get()
        use_mirror = self.use_mirror_var.get()
        if target_os == "macos":
            brew_install_cmd = 'export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git" && /bin/bash -c "$(curl -fsSL https://gitee.com/cunkai/HomebrewCN/raw/master/Homebrew.sh)"' if use_mirror else '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            cmd = f"""
            echo "开始安装 Node.js..."
            if ! command -v brew >/dev/null 2>&1; then
                echo "未检测到 Homebrew，正在拉取安装脚本..."
                {brew_install_cmd}
            fi
            brew install node
            echo "安装完成，检查版本："
            node -v
            """
        else:
            cmd = "echo 正在通过 winget 静默安装 Node.js... & winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements & echo 安装执行结束。"
        self.run_command_in_bg("安装 Node.js", cmd)

    def cmd_install_git(self):
        """单独安装 Git"""
        target_os = self.os_var.get()
        if target_os == "macos":
            cmd = """
            echo "开始安装 Git..."
            brew install git
            echo "安装完成，检查版本："
            git --version
            """
        else:
            cmd = "echo 正在通过 winget 静默安装 Git... & winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements & echo 安装执行结束。"
        self.run_command_in_bg("安装 Git", cmd)

    def cmd_install_openclaw(self):
        # 根据是否选择镜像决定是否配置 npm registry
        use_mirror = self.use_mirror_var.get()
        target_os = self.os_var.get()
        
        if use_mirror:
            if target_os == "windows":
                cmd = "npm config set registry https://registry.npmmirror.com && npm install -g openclaw"
            else:
                cmd = "npm config set registry https://registry.npmmirror.com && npm install -g openclaw"
        else:
            if target_os == "windows":
                cmd = "npm config delete registry && npm install -g openclaw"
            else:
                cmd = "npm config delete registry && npm install -g openclaw"
                
        self.run_command_in_bg("安装 OpenClaw", cmd)

    def cmd_test_openclaw(self):
        self.run_command_in_bg("测试安装", "openclaw --version")
        
    def cmd_install_gateway(self):
        self.run_command_in_bg("注册后台网关服务", "openclaw gateway install")

    # ================= Layer 2 功能 =================
    def cmd_start_service(self):
        # 先自动 check 状态，然后再启动
        cmd = "openclaw gateway start && openclaw gateway status"
        self.run_command_in_bg("启动服务", cmd)

    def cmd_stop_service(self):
        cmd = "openclaw gateway stop && openclaw gateway status"
        self.run_command_in_bg("停止服务", cmd)

    def cmd_check_status(self):
        cmd = "openclaw gateway status && openclaw --version"
        self.run_command_in_bg("查看状态", cmd)

    def cmd_open_webui(self):
        port = self.cfg_vars['port'].get() or "18789"
        # 如果有保存的 token，自动带上免密登录
        if hasattr(self, 'gateway_token') and self.gateway_token:
            url = f"http://127.0.0.1:{port}/?token={self.gateway_token}"
        else:
            url = f"http://127.0.0.1:{port}/"
        
        target_os = self.os_var.get()
        
        if target_os == "windows":
            cmd = f"start {url}"
        else:
            cmd = f"open {url}"
            
        self.run_command_in_bg("打开 WebUI", cmd)

    def cmd_save_config(self):
        """保存并应用配置 (通过终端执行文件写入完整规范模板)"""
        import secrets
        
        # 生成一个随机的 gateway token
        gateway_token = secrets.hex(20)
        
        # 完整的、经过验证的 OpenClaw 标准配置模板
        config_template = {
            "meta": {
                "lastTouchedVersion": "2026.2.25",
                "lastTouchedAt": "2026-02-28T07:18:58.181Z"
            },
            "env": {
                "MINIMAX_API_KEY": self.cfg_vars['api_key'].get() or "",
                "GEMINI_API_KEY": ""
            },
            "wizard": {
                "lastRunAt": "2026-02-28T07:18:58.159Z",
                "lastRunVersion": "2026.2.25",
                "lastRunCommand": "doctor",
                "lastRunMode": "local"
            },
            "models": {
                "mode": "merge",
                "providers": {
                    "minimax": {
                        "baseUrl": self.cfg_vars['api_url'].get() or "https://api.minimax.chat/v1",
                        "apiKey": "${MINIMAX_API_KEY}",
                        "api": "openai-completions",
                        "models": [
                            {
                                "id": self.cfg_vars['model_name'].get() or "MiniMax-M2.1",
                                "name": self.cfg_vars['model_name'].get() or "MiniMax M2.1",
                                "reasoning": False,
                                "input": ["text"],
                                "contextWindow": 200000,
                                "maxTokens": 8192
                            }
                        ]
                    }
                }
            },
            "agents": {
                "defaults": {
                    "model": {
                        "primary": f"minimax/{self.cfg_vars['model_name'].get() or 'MiniMax-M2.1'}"
                    },
                    "models": {
                        f"minimax/{self.cfg_vars['model_name'].get() or 'MiniMax-M2.1'}": {}
                    },
                    "workspace": "~\\.openclaw\\workspace",
                    "compaction": {
                        "mode": "safeguard"
                    }
                }
            },
            "commands": {
                "native": "auto",
                "nativeSkills": "auto",
                "restart": True,
                "ownerDisplay": "raw"
            },
            "gateway": {
                "mode": "local",
                "port": int(self.cfg_vars['port'].get() or 18789),
                "auth": {
                    "mode": "token",
                    "token": gateway_token
                }
            },
            "plugins": {
                "entries": {}
            }
        }
        
        json_str = json.dumps(config_template, ensure_ascii=False, indent=2)
        target_os = self.os_var.get()

        if target_os == "macos":
            cmd = f"""
mkdir -p ~/.openclaw
cat << 'EOF' > ~/.openclaw/openclaw.json
{json_str}
EOF
echo "✅ 完整规范配置已成功写入 ~/.openclaw/openclaw.json"
            """.strip()
        else:
            config_dir_win = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), '.openclaw')
            config_file_win = os.path.join(config_dir_win, 'openclaw.json')
            json_inline = json.dumps(config_template, ensure_ascii=False).replace("'", "\\'")
            safe_dir = config_dir_win.replace('\\', '\\\\')
            safe_file = config_file_win.replace('\\', '\\\\')
            cmd = f"""
python -c "import os, json; os.makedirs(r'{safe_dir}', exist_ok=True); f=open(r'{safe_file}', 'w', encoding='utf-8'); f.write('{json_inline}'); f.close(); print('✅ 完整规范配置已成功写入')"
            """.strip()

        self.run_command_in_bg("保存并应用配置", cmd)
        
        # 保存 token 到实例变量，供打开 WebUI 时使用
        self.gateway_token = gateway_token
        
        messagebox.showinfo("成功", f"【{target_os.upper()}】完整规范配置已写入！\n\nGateway Token: {gateway_token}\n\n请点击启动服务后再打开 WebUI。")

    def load_config(self):
        """应用启动时，尝试本地读取一下配置填充到 GUI"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    for key, var in self.cfg_vars.items():
                        if key in config_data:
                            var.set(str(config_data[key]))
            except Exception as e:
                print(f"读取配置失败: {e}")

if __name__ == '__main__':
    if not HAS_TKINTER:
        sys.exit(1)
    root = tk.Tk()
    app = OpenClawApp(root)
    root.mainloop()
