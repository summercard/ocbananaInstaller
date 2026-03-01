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
        # 像素风格霓虹灯标题
        title_frame = tk.Frame(self.layer1_frame, bg="#1a1a2e")
        title_frame.pack(pady=10)
        
        # 霓虹灯标题文字
        self.title_label = tk.Label(
            title_frame,
            text="◢◤ OpenClaw 傻瓜安装器 ◢◤",
            font=("Courier New", 22, "bold"),
            bg="#1a1a2e",
            fg="#00ffaa"
        )
        self.title_label.pack()
        
        # 启动霓虹灯闪烁动画
        self.neon_animation()
        
        desc = ttk.Label(self.layer1_frame, text="为了保证稳定，请按顺序分别检查和安装：", font=('Helvetica', 12))
        desc.pack(pady=5)
        
        btn_frame = ttk.Frame(self.layer1_frame)
        btn_frame.pack(pady=5)
        
        btn_style = {'ipadx': 10, 'ipady': 5, 'pady': 3, 'fill': tk.X}
        
        # 按钮顺序：每个命令行一个按钮
        btn0 = ttk.Button(btn_frame, text="1. 检查环境 (查看是否已安装 Node.js 和 Git)", command=self.cmd_check_deps)
        btn0.pack(**btn_style)

        btn1 = ttk.Button(btn_frame, text="2. 安装 Node.js (使用 winget 静默安装)", command=self.cmd_install_node)
        btn1.pack(**btn_style)
        
        btn2 = ttk.Button(btn_frame, text="3. 刷新环境变量 (需手动关闭CMD重开)", command=self.cmd_refresh_env)
        btn2.pack(**btn_style)
        
        btn3 = ttk.Button(btn_frame, text="4. 安装 Git (若步骤1提示缺失则点击)", command=self.cmd_install_git)
        btn3.pack(**btn_style)
        
        btn4 = ttk.Button(btn_frame, text="5. 安装 OpenClaw 核心 (npm install -g openclaw-cn)", command=self.cmd_install_openclaw)
        btn4.pack(**btn_style)
        
        btn5 = ttk.Button(btn_frame, text="6. 测试安装 (查看 OpenClaw 版本)", command=self.cmd_test_openclaw)
        btn5.pack(**btn_style)

        # 第六步之后、第七步之前：生成 Gateway 配置模板
        btn6_pre = ttk.Button(btn_frame, text="6.5 生成 Gateway 配置模板 (必须先执行)", command=self.cmd_gen_gateway_config)
        btn6_pre.pack(**btn_style)

        btn6 = ttk.Button(btn_frame, text="7. 注册后台网关服务 (Gateway Install)", command=self.cmd_install_gateway)
        btn6.pack(**btn_style)
        
        btn7 = ttk.Button(btn_frame, text="8. 启动 Gateway (Gateway Start)", command=self.cmd_start_gateway)
        btn7.pack(**btn_style)
        
        btn8 = ttk.Button(btn_frame, text="9. 进入控制台 (服务启停与配置) ➔", command=self.show_layer2)
        btn8.pack(ipadx=10, ipady=8, pady=8, fill=tk.X)

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

        # API 服务商配置信息
        self.api_provider_info = {
            'minimax': {
                'name': 'MiniMax',
                'provider': 'minimax',
                'baseUrl': 'https://api.minimax.chat/v1',
                'apiType': 'openai-completions',
                'envKey': 'MINIMAX_API_KEY',
                'defaultModel': 'MiniMax-M2.1',
                'input': ['text'],
                'reasoning': False,
                'contextWindow': 200000,
                'maxTokens': 8192
            },
            'bigmodel': {
                'name': 'BigModel (智谱)',
                'provider': 'bigmodel',
                'baseUrl': 'https://open.bigmodel.cn/api/paas/v4',
                'apiType': 'openai-completions',
                'envKey': 'BIGMODEL_API_KEY',
                'defaultModel': 'glm-4',
                'input': ['text'],
                'reasoning': False,
                'contextWindow': 128000,
                'maxTokens': 8192
            },
            'google': {
                'name': 'Google Gemini',
                'provider': 'google',
                'baseUrl': 'https://generativelanguage.googleapis.com/v1beta',
                'apiType': 'google-generative-ai',
                'envKey': 'GEMINI_API_KEY',
                'defaultModel': 'gemini-2.5-flash-preview-05-20',
                'input': ['text', 'image'],
                'reasoning': True,
                'contextWindow': 1000000,
                'maxTokens': 64000
            }
        }

        # 表单字段
        self.cfg_vars = {
            'api_type': tk.StringVar(value='minimax'),
            'api_url': tk.StringVar(value='https://api.minimax.chat/v1'),
            'api_key': tk.StringVar(),
            'model_name': tk.StringVar(value='MiniMax-M2.1'),
            'port': tk.StringVar(value='18789')
        }

        # 当选择不同的 API 服务商时，自动填充对应的 URL
        def on_api_type_change(*args):
            api_type = self.cfg_vars['api_type'].get()
            if api_type in self.api_provider_info:
                info = self.api_provider_info[api_type]
                self.cfg_vars['api_url'].set(info['baseUrl'])
                self.cfg_vars['model_name'].set(info['defaultModel'])

        self.cfg_vars['api_type'].trace('w', on_api_type_change)

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
                cb = ttk.Combobox(f, textvariable=self.cfg_vars[var_name], values=['minimax', 'bigmodel', 'google'], state='readonly')
                cb.pack(side=tk.LEFT, fill=tk.X, expand=True)
            elif var_name == 'api_key':
                ttk.Entry(f, textvariable=self.cfg_vars[var_name], show="*").pack(side=tk.LEFT, fill=tk.X, expand=True)
            else:
                ttk.Entry(f, textvariable=self.cfg_vars[var_name]).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 两个按钮：新增 API 服务 和 更新 API
        btn_frame = ttk.Frame(cfg_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="➕ 新增 API 服务", command=self.cmd_add_api_service).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 更新已有 API", command=self.cmd_update_api).pack(side=tk.LEFT, padx=5)

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

    def cmd_gen_gateway_config(self):
        """修补 Gateway 配置文件（只添加缺少的 mode 和 port 字段，避免启动失败）"""
        import secrets
        import os
        import json

        # 生成随机 Gateway Token（如果已有则保留）
        if hasattr(self, 'gateway_token') and self.gateway_token:
            gateway_token = self.gateway_token
        else:
            gateway_token = secrets.token_hex(20)

        target_os = self.os_var.get()

        # 直接在 Python 中修补配置（避免命令转义问题）
        def patch_config():
            try:
                if target_os == "windows":
                    config_file = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), '.openclaw', 'openclaw.json')
                else:
                    config_file = os.path.expanduser('~/.openclaw/openclaw.json')

                os.makedirs(os.path.dirname(config_file), exist_ok=True)

                # 读取现有配置或创建新配置
                if os.path.exists(config_file) and os.path.getsize(config_file) > 0:
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except:
                        config = {}
                else:
                    config = {}

                # 只修补缺少的字段
                if 'commands' not in config:
                    config['commands'] = {'native': 'auto', 'nativeSkills': 'auto', 'restart': True, 'ownerDisplay': 'raw'}

                if 'gateway' not in config:
                    config['gateway'] = {}
                if 'mode' not in config.get('gateway', {}):
                    config['gateway']['mode'] = 'local'
                if 'port' not in config.get('gateway', {}):
                    config['gateway']['port'] = 18789
                if 'auth' not in config.get('gateway', {}):
                    config['gateway']['auth'] = {'mode': 'token', 'token': gateway_token}
                if 'token' not in config.get('gateway', {}).get('auth', {}):
                    config['gateway']['auth']['token'] = gateway_token

                if 'meta' not in config:
                    config['meta'] = {'lastTouchedVersion': '2026.2.26', 'lastTouchedAt': '2026-03-01T00:00:00.000Z'}

                # 写回文件
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                self.log_terminal(f"✅ Gateway 配置修补完成！Token: {gateway_token}\n文件: {config_file}\n")
                return True
            except Exception as e:
                self.log_terminal(f"❌ 配置修补失败: {str(e)}\n")
                return False

        # 保存 token 供后续使用
        self.gateway_token = gateway_token

        # 在后台线程执行修补
        def task():
            success = patch_config()
            if success:
                self.root.after(100, lambda: messagebox.showinfo("配置修补", f"Gateway 配置修补完成！\n\n已添加缺少的字段：\n- gateway.mode = local\n- gateway.port = 18789\n\nToken: {gateway_token}\n\n请在后续步骤启动 Gateway。"))

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

    def cmd_install_gateway(self):
        self.run_command_in_bg("注册后台网关服务", "openclaw gateway install")

    def cmd_refresh_env(self):
        """刷新环境变量（Windows 提醒手动操作）"""
        target_os = self.os_var.get()
        if target_os == "windows":
            msg = "⚠️  重要提示：安装 Node.js 后，需要刷新环境变量\n\n" \
                  "请执行以下操作：\n" \
                  "1. 关闭当前 CMD 窗口\n" \
                  "2. 重新以管理员身份打开一个新的 CMD 窗口\n" \
                  "3. 在新窗口中验证：node --version\n\n" \
                  "完成后继续下一步安装"
            self.run_command_in_bg("刷新环境变量", f'echo "{msg}"')
        else:
            self.run_command_in_bg("刷新环境变量", 'echo "macOS/Linux 无需手动刷新环境变量"')

    def cmd_start_gateway(self):
        """启动 Gateway"""
        self.run_command_in_bg("启动 Gateway", "openclaw gateway start")

    def neon_animation(self):
        """像素风格霓虹灯闪烁动画"""
        colors = ["#00ffaa", "#ff00ff", "#00ffff", "#ffff00", "#ff6600"]
        current_idx = [0]
        glow_phase = [0]
        
        def animate():
            try:
                phase = int(glow_phase[0]) % 3
                if phase == 0:
                    self.title_label.config(fg=colors[current_idx[0]], text="◢◤ OpenClaw 傻瓜安装器 ◢◤")
                    glow_phase[0] += 1
                elif phase == 1:
                    glow_phase[0] += 1
                else:
                    self.title_label.config(fg="#004433", text="◢◤ OpenClaw 傻瓜安装器 ◢◤")
                    current_idx[0] = (current_idx[0] + 1) % len(colors)
                    glow_phase[0] = 0
                self.title_label.after(500, animate)
            except:
                pass
        animate()

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

    def cmd_add_api_service(self):
        """新增 API 服务（在原有配置基础上增加一个新的 API 模型）"""
        import os
        import json
        import secrets

        target_os = self.os_var.get()
        api_type = self.cfg_vars['api_type'].get()
        api_url = self.cfg_vars['api_url'].get()
        api_key = self.cfg_vars['api_key'].get()
        model_name = self.cfg_vars['model_name'].get()
        port = self.cfg_vars['port'].get() or '18789'

        # 获取 API 服务商配置
        if api_type not in self.api_provider_info:
            messagebox.showerror("错误", f"不支持的 API 服务商: {api_type}")
            return

        provider_info = self.api_provider_info[api_type]
        env_key = provider_info['envKey']

        # 生成 gateway token
        gateway_token = secrets.token_hex(20)

        def patch_config():
            try:
                if target_os == "windows":
                    config_file = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), '.openclaw', 'openclaw.json')
                else:
                    config_file = os.path.expanduser('~/.openclaw/openclaw.json')

                os.makedirs(os.path.dirname(config_file), exist_ok=True)

                # 读取现有配置
                if os.path.exists(config_file) and os.path.getsize(config_file) > 0:
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except:
                        config = {}
                else:
                    config = {}

                # 确保基本结构存在
                if 'commands' not in config:
                    config['commands'] = {'native': 'auto', 'nativeSkills': 'auto', 'restart': True, 'ownerDisplay': 'raw'}
                if 'gateway' not in config:
                    config['gateway'] = {'mode': 'local', 'port': int(port), 'auth': {'mode': 'token', 'token': gateway_token}}
                if 'meta' not in config:
                    config['meta'] = {'lastTouchedVersion': '2026.2.26', 'lastTouchedAt': '2026-03-01T00:00:00.000Z'}
                if 'env' not in config:
                    config['env'] = {}
                if 'models' not in config:
                    config['models'] = {'mode': 'merge', 'providers': {}}
                if 'agents' not in config:
                    config['agents'] = {'defaults': {'workspace': '~/.openclaw/workspace', 'compaction': {'mode': 'safeguard'}}}

                # 设置 env 中的 API Key
                # 清理 API Key，去除换行和空白
                api_key_clean = api_key.strip().replace('\n', '').replace('\r', '')
                config['env'][env_key] = api_key_clean

                # 添加 models.providers
                if 'providers' not in config['models']:
                    config['models']['providers'] = {}

                # 获取 provider 名称（用于配置文件中的 key）
                provider_name = provider_info.get('provider', api_type)
                api_type_value = provider_info.get('apiType', 'openai-completions')

                # 构建 provider 配置
                config['models']['providers'][provider_name] = {
                    'baseUrl': api_url,
                    'apiKey': f'${{{env_key}}}',
                    'api': api_type_value,
                    'models': [
                        {
                            'id': model_name,
                            'name': model_name,
                            'reasoning': provider_info.get('reasoning', False),
                            'input': provider_info.get('input', ['text']),
                            'contextWindow': provider_info.get('contextWindow', 128000),
                            'maxTokens': provider_info.get('maxTokens', 4096)
                        }
                    ]
                }

                # 设置默认模型
                config['agents']['defaults']['model'] = {'primary': f'{provider_name}/{model_name}'}
                if 'models' not in config['agents']['defaults']:
                    config['agents']['defaults']['models'] = {}
                config['agents']['defaults']['models'][f'{provider_name}/{model_name}'] = {}

                # 写回文件
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                self.log_terminal(f"✅ 新增 API 服务完成！\nAPI 类型: {api_type}\n模型: {model_name}\n文件: {config_file}\n")
                return True
            except Exception as e:
                self.log_terminal(f"❌ 新增 API 服务失败: {str(e)}\n")
                return False

        # 保存 token
        self.gateway_token = gateway_token

        # 在后台线程执行
        def task():
            success = patch_config()
            if success:
                self.root.after(100, lambda: messagebox.showinfo("成功", f"✅ 新增 API 服务完成！\n\nAPI 服务商: {api_type}\n模型: {model_name}\n\nGateway Token: {gateway_token}\n\n请重启 Gateway 服务后生效。"))

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

    def cmd_update_api(self):
        """更新 API（在原有配置基础上更新已有字段）"""
        import os
        import json
        import secrets

        target_os = self.os_var.get()
        api_type = self.cfg_vars['api_type'].get()
        api_url = self.cfg_vars['api_url'].get()
        api_key = self.cfg_vars['api_key'].get()
        model_name = self.cfg_vars['model_name'].get()
        port = self.cfg_vars['port'].get() or '18789'

        # 获取 API 服务商配置
        if api_type not in self.api_provider_info:
            messagebox.showerror("错误", f"不支持的 API 服务商: {api_type}")
            return

        provider_info = self.api_provider_info[api_type]
        env_key = provider_info['envKey']

        # 生成 gateway token（保留原有的如果有）
        gateway_token = secrets.token_hex(20)

        def patch_config():
            try:
                if target_os == "windows":
                    config_file = os.path.join(os.environ.get('USERPROFILE', 'C:\\'), '.openclaw', 'openclaw.json')
                else:
                    config_file = os.path.expanduser('~/.openclaw/openclaw.json')

                os.makedirs(os.path.dirname(config_file), exist_ok=True)

                # 读取现有配置
                if os.path.exists(config_file) and os.path.getsize(config_file) > 0:
                    try:
                        with open(config_file, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                    except:
                        config = {}
                else:
                    config = {}

                # 确保基本结构存在
                if 'commands' not in config:
                    config['commands'] = {'native': 'auto', 'nativeSkills': 'auto', 'restart': True, 'ownerDisplay': 'raw'}
                if 'gateway' not in config:
                    config['gateway'] = {'mode': 'local', 'port': int(port), 'auth': {'mode': 'token', 'token': gateway_token}}
                else:
                    # 保留原有的 gateway token
                    if 'auth' in config.get('gateway', {}) and 'token' in config['gateway']['auth']:
                        gateway_token = config['gateway']['auth']['token']
                if 'meta' not in config:
                    config['meta'] = {'lastTouchedVersion': '2026.2.26', 'lastTouchedAt': '2026-03-01T00:00:00.000Z'}
                if 'env' not in config:
                    config['env'] = {}
                if 'models' not in config:
                    config['models'] = {'mode': 'merge', 'providers': {}}
                if 'agents' not in config:
                    config['agents'] = {'defaults': {'workspace': '~/.openclaw/workspace', 'compaction': {'mode': 'safeguard'}}}

                # 更新 env 中的 API Key
                # 清理 API Key，去除换行和空白
                api_key_clean = api_key.strip().replace('\n', '').replace('\r', '')
                config['env'][env_key] = api_key_clean

                # 获取 provider 名称（用于配置文件中的 key）
                provider_name = provider_info.get('provider', api_type)
                api_type_value = provider_info.get('apiType', 'openai-completions')

                # 更新 models.providers
                if 'providers' not in config['models']:
                    config['models']['providers'] = {}

                # 更新或添加 provider 配置
                config['models']['providers'][provider_name] = {
                    'baseUrl': api_url,
                    'apiKey': f'${{{env_key}}}',
                    'api': api_type_value,
                    'models': [
                        {
                            'id': model_name,
                            'name': model_name,
                            'reasoning': provider_info.get('reasoning', False),
                            'input': provider_info.get('input', ['text']),
                            'contextWindow': provider_info.get('contextWindow', 128000),
                            'maxTokens': provider_info.get('maxTokens', 4096)
                        }
                    ]
                }

                # 更新默认模型
                config['agents']['defaults']['model'] = {'primary': f'{provider_name}/{model_name}'}
                if 'models' not in config['agents']['defaults']:
                    config['agents']['defaults']['models'] = {}
                config['agents']['defaults']['models'][f'{provider_name}/{model_name}'] = {}

                # 写回文件
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)

                self.log_terminal(f"✅ 更新 API 完成！\nAPI 类型: {api_type}\n模型: {model_name}\n文件: {config_file}\n")
                return True
            except Exception as e:
                self.log_terminal(f"❌ 更新 API 失败: {str(e)}\n")
                return False

        # 保存 token
        self.gateway_token = gateway_token

        # 在后台线程执行
        def task():
            success = patch_config()
            if success:
                self.root.after(100, lambda: messagebox.showinfo("成功", f"✅ 更新 API 完成！\n\nAPI 服务商: {api_type}\n模型: {model_name}\n\n请重启 Gateway 服务后生效。"))

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

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
