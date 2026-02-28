"""
主窗口
OpenClawInstaller的主界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from typing import Optional
import os
from utils.logger import get_logger
from core.config import Config
from core.installer import Installer

# 获取资源目录
def get_asset_path(filename):
    """获取资源文件路径"""
    return os.path.join(os.path.dirname(__file__), 'assets', filename)

def setup_styles():
    """设置自定义样式"""
    style = ttk.Style()
    
    # 尝试使用 dark 主题
    try:
        style.theme_use('clam')
    except:
        pass
    
    # 配置样式
    style.configure('TFrame', background='#1a1a2e')
    style.configure('TLabel', background='#1a1a2e', foreground='#ffffff')
    style.configure('TLabelframe', background='#16213e', foreground='#ffffff')
    style.configure('TLabelframe.Label', background='#16213e', foreground='#00d9ff', font=('微软雅黑', 10, 'bold'))
    style.configure('TButton', background='#0f3460', foreground='#ffffff', font=('微软雅黑', 10))
    
    return style

class MainWindow:
    """主窗口类"""

    def __init__(self, root: tk.Tk):
        """
        初始化主窗口

        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.logger = get_logger()

        # 设置样式
        setup_styles()
        
        # 当前页面
        self.current_page = None

        # 创建UI
        self._setup_window()
        self._create_layout()
        self._create_pages()

        self.logger.info("主窗口已初始化")

    def _setup_window(self):
        """设置窗口属性"""
        # 窗口标题
        self.root.title("OpenClaw跨平台安装工具")

        # 窗口大小
        self.root.geometry("900x650")
        self.root.minsize(800, 600)

        # 设置窗口图标
        icon_path = get_asset_path('icon3.png')
        if os.path.exists(icon_path):
            try:
                icon = tk.PhotoImage(file=icon_path)
                self.root.iconphoto(False, icon)
            except Exception as e:
                self.logger.warning(f"无法加载图标: {e}")

        # 窗口居中
        self._center_window()

        # 设置背景图片
        self._set_background()

    def _set_background(self):
        """设置背景图片"""
        bg_path = get_asset_path('scree.png')
        if os.path.exists(bg_path):
            try:
                self.bg_image = tk.PhotoImage(file=bg_path)
                # 获取屏幕尺寸
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                # 创建背景标签
                bg_label = tk.Label(self.root, image=self.bg_image)
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.bg_label = bg_label
            except Exception as e:
                self.logger.warning(f"无法加载背景图片: {e}")
                # 使用纯色背景
                self.root.configure(bg='#2d2d2d')

    def _center_window(self):
        """窗口居中显示"""
        self.root.update_idletasks()

        # 获取窗口尺寸
        width = self.root.winfo_width()
        height = self.root.winfo_height()

        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口位置
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _create_layout(self):
        """创建窗口布局"""
        # 创建内容容器（覆盖在背景之上）
        self.content_container = tk.Frame(self.root, bg='#1a1a2e')
        self.content_container.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # 主框架
        self.main_frame = tk.Frame(self.content_container, bg='#1a1a2e')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # 顶部标题区域
        self._create_header()

        # 顶部导航栏
        self.nav_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        self.nav_frame.pack(fill=tk.X, pady=(10, 15))

        # 内容区域
        self.content_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 底部日志区域
        self.log_frame = tk.LabelFrame(self.main_frame, text="日志输出", fg='#ffffff', bg='#1a1a2e', font=('微软雅黑', 10))
        self.log_frame.pack(fill=tk.X, pady=(10, 0))

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=8,
            wrap=tk.WORD,
            state='disabled',
            bg='#16213e',
            fg='#eaeaea',
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

        # 创建导航按钮
        self._create_navigation()

    def _create_header(self):
        """创建顶部标题"""
        header_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        header_frame.pack(fill=tk.X)
        
        # 加载标题图片
        header_img_path = get_asset_path('002.png')
        if os.path.exists(header_img_path):
            try:
                self.header_image = tk.PhotoImage(file=header_img_path)
                header_label = tk.Label(header_frame, image=self.header_image, bg='#1a1a2e')
                header_label.pack(pady=(0, 10))
            except Exception as e:
                # 图片加载失败，使用文字标题
                title_label = tk.Label(
                    header_frame,
                    text="OpenClaw 安装工具",
                    font=('微软雅黑', 24, 'bold'),
                    fg='#00d9ff',
                    bg='#1a1a2e'
                )
                title_label.pack(pady=(0, 10))
        else:
            title_label = tk.Label(
                header_frame,
                text="OpenClaw 安装工具",
                font=('微软雅黑', 24, 'bold'),
                fg='#00d9ff',
                bg='#1a1a2e'
            )
            title_label.pack(pady=(0, 10))

    def _create_navigation(self):
        """创建导航按钮"""
        # 导航按钮配置
        nav_buttons = [
            ("安装", "install", lambda: self._show_page("install")),
            ("配置", "config", lambda: self._show_page("config")),
            ("状态", "status", lambda: self._show_page("status"))
        ]

        self.nav_buttons = {}

        # 创建按钮样式
        style = ttk.Style()
        style.configure('Nav.TButton', font=('微软雅黑', 12), padding=10)
        
        # 创建按钮
        for i, (text, name, command) in enumerate(nav_buttons):
            btn = tk.Button(
                self.nav_frame,
                text=text,
                command=command,
                width=12,
                font=('微软雅黑', 12, 'bold'),
                bg='#0f3460',
                fg='#ffffff',
                activebackground='#00d9ff',
                activeforeground='#000000',
                relief='flat',
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=(0, 10))
            self.nav_buttons[name] = btn

        # 默认选中第一个按钮
        self._select_nav_button("install")

    def _create_pages(self):
        """创建所有页面"""
        self.pages = {}

        # 导入页面类（这里先创建占位符）
        # from .install_page import InstallPage
        # from .config_page import ConfigPage
        # from .status_page import StatusPage

        # 创建安装页面
        self.pages["install"] = self._create_install_page()

        # 创建配置页面
        self.pages["config"] = self._create_config_page()

        # 创建状态页面
        self.pages["status"] = self._create_status_page()

        # 默认显示安装页面
        self._show_page("install")

    def _create_install_page(self):
        """创建安装页面"""
        frame = tk.Frame(self.content_frame, bg='#1a1a2e')

        # 标题
        title_label = tk.Label(
            frame,
            text="OpenClaw 安装",
            font=('微软雅黑', 20, 'bold'),
            fg='#00d9ff',
            bg='#1a1a2e'
        )
        title_label.pack(pady=20)

        # 环境检查结果区域
        env_frame = tk.LabelFrame(frame, text="环境检查", fg='#ffffff', bg='#16213e', font=('微软雅黑', 11, 'bold'))
        env_frame.pack(fill=tk.X, padx=10, pady=10)

        # 环境检查结果显示
        self.env_results = {}
        env_checks = [
            ("Python版本", "python_version"),
            ("Node.js版本", "nodejs_version"),
            ("磁盘空间", "disk_space"),
            ("网络连接", "network")
        ]

        for i, (label_text, key) in enumerate(env_checks):
            row_frame = ttk.Frame(env_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)

            label = ttk.Label(row_frame, text=label_text, width=15)
            label.pack(side=tk.LEFT, padx=(0, 10))

            result_label = ttk.Label(row_frame, text="待检查")
            result_label.pack(side=tk.LEFT)

            self.env_results[key] = result_label

        # 安装按钮
        self.install_button = ttk.Button(
            frame,
            text="开始安装",
            command=lambda: self._start_install()
        )
        self.install_button.pack(pady=20)

        # 进度条
        self.progress_frame = ttk.Frame(frame)
        self.progress_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack()

        self.progress_label = ttk.Label(self.progress_frame, text="")
        self.progress_label.pack(pady=5)

        return frame

    def _create_config_page(self) -> ttk.Frame:
        """创建配置页面"""
        frame = ttk.Frame(self.content_frame)

        # 标题
        title_label = ttk.Label(
            frame,
            text="OpenClaw配置",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # 配置表单区域
        config_frame = ttk.LabelFrame(frame, text="配置项")
        config_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 配置项
        self.config_vars = {}

        # 安装目录（可选择）
        install_dir_row = ttk.Frame(config_frame)
        install_dir_row.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(install_dir_row, text="安装目录", width=15).pack(side=tk.LEFT, padx=(0, 10))

        self.config_vars["install_dir"] = tk.StringVar()
        entry = ttk.Entry(install_dir_row, textvariable=self.config_vars["install_dir"], width=25)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(
            install_dir_row,
            text="浏览...",
            command=lambda: self._select_install_dir()
        ).pack(side=tk.LEFT, padx=(5, 0))

        # ==================== API 配置区域 ====================
        api_config_frame = ttk.LabelFrame(config_frame, text="API 配置")
        api_config_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # API 类型选择
        api_type_row = ttk.Frame(api_config_frame)
        api_type_row.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(api_type_row, text="API 类型", width=15).pack(side=tk.LEFT, padx=(0, 10))

        self.config_vars["api_type"] = tk.StringVar(value="minimax")
        api_type_combo = ttk.Combobox(
            api_type_row,
            textvariable=self.config_vars["api_type"],
            values=["minimax", "anthropic", "openai", "custom"],
            state="readonly",
            width=15
        )
        api_type_combo.pack(side=tk.LEFT)
        api_type_combo.bind("<<ComboboxSelected>>", self._on_api_type_changed)

        # API 地址
        api_url_row = ttk.Frame(api_config_frame)
        api_url_row.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(api_url_row, text="API 地址", width=15).pack(side=tk.LEFT, padx=(0, 10))

        self.config_vars["api_url"] = tk.StringVar()
        entry = ttk.Entry(api_url_row, textvariable=self.config_vars["api_url"], width=35)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # API Key
        api_key_row = ttk.Frame(api_config_frame)
        api_key_row.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(api_key_row, text="API Key", width=15).pack(side=tk.LEFT, padx=(0, 10))

        self.config_vars["api_key"] = tk.StringVar()
        self.api_key_entry = ttk.Entry(api_key_row, textvariable=self.config_vars["api_key"], width=35, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 显示/隐藏 API Key
        self.api_key_visible = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            api_key_row,
            text="显示",
            variable=self.api_key_visible,
            command=self._toggle_api_key_visibility
        ).pack(side=tk.LEFT, padx=(5, 0))

        # 模型名称
        model_name_row = ttk.Frame(api_config_frame)
        model_name_row.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(model_name_row, text="模型名称", width=15).pack(side=tk.LEFT, padx=(0, 10))

        self.config_vars["model_name"] = tk.StringVar()
        entry = ttk.Entry(model_name_row, textvariable=self.config_vars["model_name"], width=35)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # ==================== 自动启动 ====================
        auto_start_row = ttk.Frame(config_frame)
        auto_start_row.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(auto_start_row, text="自动启动", width=15).pack(side=tk.LEFT, padx=(0, 10))

        var = tk.BooleanVar()
        self.config_vars["auto_start"] = var
        ttk.Checkbutton(auto_start_row, variable=var).pack(side=tk.LEFT)

        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="保存配置",
            command=lambda: self._save_config()
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="加载配置",
            command=lambda: self._load_config()
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def _create_status_page(self) -> ttk.Frame:
        """创建状态页面"""
        frame = ttk.Frame(self.content_frame)

        # 标题
        title_label = ttk.Label(
            frame,
            text="OpenClaw状态",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # 状态信息区域
        status_frame = ttk.LabelFrame(frame, text="运行状态")
        status_frame.pack(fill=tk.X, padx=20, pady=10)

        # 状态显示
        self.status_vars = {}
        status_items = [
            ("运行状态", "running", "未运行"),
            ("端口", "port", "-"),
            ("PID", "pid", "-"),
            ("版本", "version", "-"),
            ("安装路径", "path", "-")
        ]

        for i, (label_text, key, default) in enumerate(status_items):
            row_frame = ttk.Frame(status_frame)
            row_frame.pack(fill=tk.X, padx=10, pady=5)

            label = ttk.Label(row_frame, text=label_text, width=15)
            label.pack(side=tk.LEFT, padx=(0, 10))

            var = tk.StringVar(value=default)
            result_label = ttk.Label(row_frame, textvariable=var)
            result_label.pack(side=tk.LEFT)

            self.status_vars[key] = var

        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        ttk.Button(
            button_frame,
            text="启动",
            command=lambda: self._start_openclaw()
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="停止",
            command=lambda: self._stop_openclaw()
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="打开Web界面",
            command=lambda: self._open_webui()
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="刷新状态",
            command=lambda: self._refresh_status()
        ).pack(side=tk.LEFT, padx=5)

        return frame

    def _show_page(self, page_name: str):
        """显示指定页面"""
        # 隐藏所有页面
        for name, page in self.pages.items():
            page.pack_forget()

        # 显示指定页面
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name

            # 更新导航按钮状态
            self._select_nav_button(page_name)

    def _select_nav_button(self, selected_name: str):
        """选中导航按钮"""
        # TODO: 实现按钮选中状态样式
        pass

    def _start_install(self):
        """开始安装"""
        self.logger.info("开始安装...")
        self._log_message("开始安装OpenClaw...")

        # TODO: 调用installer.install()

        # 显示进度条
        self.progress_bar.start(10)
        self.progress_label.config(text="正在安装...")

    def _select_install_dir(self):
        """选择安装目录"""
        directory = filedialog.askdirectory(
            title="选择安装目录",
            initialdir=self.config_vars["install_dir"].get() or "~"
        )
        if directory:
            self.config_vars["install_dir"].set(directory)
            self.logger.info(f"选择安装目录: {directory}")

    def _on_api_type_changed(self, event=None):
        """API类型变更时自动填充默认配置"""
        api_type = self.config_vars["api_type"].get()
        
        # 根据API类型预设默认配置
        defaults = {
            "minimax": {
                "url": "https://api.minimax.chat/v1",
                "model": "MiniMax-M2.1"
            },
            "anthropic": {
                "url": "https://api.anthropic.com",
                "model": "claude-sonnet-4-5"
            },
            "openai": {
                "url": "https://api.openai.com/v1",
                "model": "gpt-4o"
            },
            "custom": {
                "url": "",
                "model": ""
            }
        }
        
        if api_type in defaults:
            if not self.config_vars["api_url"].get():  # 只在空的时候填充
                self.config_vars["api_url"].set(defaults[api_type]["url"])
            if not self.config_vars["model_name"].get():
                self.config_vars["model_name"].set(defaults[api_type]["model"])

    def _toggle_api_key_visibility(self):
        """切换API Key显示/隐藏"""
        if self.api_key_visible.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def _save_config(self):
        """保存配置"""
        self.logger.info("保存配置...")
        try:
            config = Config()
            config.load()

            # 读取GUI中的配置
            install_dir = self.config_vars["install_dir"].get()
            api_type = self.config_vars["api_type"].get()
            api_url = self.config_vars["api_url"].get()
            api_key = self.config_vars["api_key"].get()
            model_name = self.config_vars["model_name"].get()
            auto_start = self.config_vars["auto_start"].get()

            # 保存安装目录
            if install_dir:
                config.set("openclaw.install_dir", install_dir)
                config.set("paths.openclaw", install_dir)

            # 保存自动启动
            config.set("openclaw.auto_start", auto_start)

            # 保存API配置到 OpenClaw 的配置文件
            self._save_openclaw_config(api_type, api_url, api_key, model_name)

            config.save()

            self._log_message(f"配置已保存")
            self.logger.info(f"配置已保存")
        except Exception as e:
            self._log_message(f"保存配置失败: {e}")
            self.logger.error(f"保存配置失败: {e}")

    def _save_openclaw_config(self, api_type, api_url, api_key, model_name):
        """保存到 OpenClaw 配置文件"""
        try:
            import json
            import os
            
            openclaw_config_path = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
            
            # 读取现有配置
            if os.path.exists(openclaw_config_path):
                with open(openclaw_config_path, 'r', encoding='utf-8') as f:
                    oc_config = json.load(f)
            else:
                oc_config = {}
            
            # 设置环境变量
            if "env" not in oc_config:
                oc_config["env"] = {}
            
            # 根据API类型设置对应的环境变量和配置
            if api_type == "minimax":
                oc_config["env"]["MINIMAX_API_KEY"] = api_key
                if "models" not in oc_config:
                    oc_config["models"] = {"mode": "merge", "providers": {}}
                oc_config["models"]["providers"]["minimax"] = {
                    "baseUrl": api_url or "https://api.minimax.chat/v1",
                    "apiKey": "${MINIMAX_API_KEY}",
                    "api": "openai-completions",
                    "models": [{"id": model_name or "MiniMax-M2.1", "name": model_name or "MiniMax M2.1", "reasoning": False, "input": ["text"], "contextWindow": 200000, "maxTokens": 8192}]
                }
                oc_config.setdefault("agents", {}).setdefault("defaults", {})["model"] = {"primary": f"minimax/{model_name or 'MiniMax-M2.1'}"}
                
            elif api_type == "anthropic":
                oc_config["env"]["ANTHROPIC_API_KEY"] = api_key
                oc_config.setdefault("agents", {}).setdefault("defaults", {})["model"] = {"primary": f"anthropic/{model_name or 'claude-sonnet-4-5'}"}
                
            elif api_type == "openai":
                oc_config["env"]["OPENAI_API_KEY"] = api_key
                oc_config.setdefault("agents", {}).setdefault("defaults", {})["model"] = {"primary": f"openai/{model_name or 'gpt-4o'}"}
            
            # 保存配置
            with open(openclaw_config_path, 'w', encoding='utf-8') as f:
                json.dump(oc_config, f, indent=2, ensure_ascii=False)
            
            self._log_message(f"OpenClaw配置已更新: {openclaw_config_path}")
            self.logger.info(f"OpenClaw配置已更新: {openclaw_config_path}")
            
        except Exception as e:
            self._log_message(f"保存OpenClaw配置失败: {e}")
            self.logger.error(f"保存OpenClaw配置失败: {e}")

    def _load_config(self):
        """加载配置"""
        self.logger.info("加载配置...")
        try:
            config = Config()
            config.load()

            # 加载安装目录
            install_dir = config.get("openclaw.install_dir", "")
            self.config_vars["install_dir"].set(install_dir)

            # 加载自动启动
            auto_start = config.get("openclaw.auto_start", False)
            self.config_vars["auto_start"].set(auto_start)

            # 从 OpenClaw 配置中加载 API 配置
            self._load_openclaw_config()

            self._log_message("配置已加载")
            self.logger.info("配置已加载")
        except Exception as e:
            self._log_message(f"加载配置失败: {e}")
            self.logger.error(f"加载配置失败: {e}")

    def _load_openclaw_config(self):
        """从 OpenClaw 配置文件加载 API 配置"""
        try:
            import json
            import os
            
            openclaw_config_path = os.path.join(os.path.expanduser("~"), ".openclaw", "openclaw.json")
            
            if os.path.exists(openclaw_config_path):
                with open(openclaw_config_path, 'r', encoding='utf-8') as f:
                    oc_config = json.load(f)
                
                # 尝试识别 API 类型并加载
                env = oc_config.get("env", {})
                
                if "MINIMAX_API_KEY" in env:
                    self.config_vars["api_type"].set("minimax")
                    providers = oc_config.get("models", {}).get("providers", {})
                    if "minimax" in providers:
                        self.config_vars["api_url"].set(providers["minimax"].get("baseUrl", ""))
                        models = providers["minimax"].get("models", [])
                        if models:
                            self.config_vars["model_name"].set(models[0].get("id", "MiniMax-M2.1"))
                    # API Key 需要用户重新输入（不存储明文）
                    
                elif "ANTHROPIC_API_KEY" in env:
                    self.config_vars["api_type"].set("anthropic")
                    self.config_vars["api_url"].set("https://api.anthropic.com")
                    agents = oc_config.get("agents", {}).get("defaults", {}).get("model", {})
                    primary = agents.get("primary", "")
                    if primary.startswith("anthropic/"):
                        self.config_vars["model_name"].set(primary.replace("anthropic/", ""))
                        
                elif "OPENAI_API_KEY" in env:
                    self.config_vars["api_type"].set("openai")
                    self.config_vars["api_url"].set("https://api.openai.com/v1")
                    agents = oc_config.get("agents", {}).get("defaults", {}).get("model", {})
                    primary = agents.get("primary", "")
                    if primary.startswith("openai/"):
                        self.config_vars["model_name"].set(primary.replace("openai/", ""))
                
        except Exception as e:
            self.logger.debug(f"加载OpenClaw配置失败: {e}")

    def _start_openclaw(self):
        """启动OpenClaw"""
        self.logger.info("启动OpenClaw...")
        self._log_message("OpenClaw已启动")

        # TODO: 实现启动逻辑

    def _stop_openclaw(self):
        """停止OpenClaw"""
        self.logger.info("停止OpenClaw...")
        self._log_message("OpenClaw已停止")

        # TODO: 实现停止逻辑

    def _open_webui(self):
        """打开Web界面"""
        self.logger.info("打开Web界面...")
        self._log_message("正在打开Web界面...")

        # TODO: 实现打开浏览器逻辑

    def _refresh_status(self):
        """刷新状态"""
        self.logger.info("刷新状态...")

        # TODO: 实现状态刷新逻辑

    def _log_message(self, message: str):
        """添加日志消息"""
        import datetime

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"

        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

        # 同时写入logger
        self.logger.info(message)

    def run(self):
        """运行主循环"""
        self.logger.info("主窗口启动")
        self.root.mainloop()


# 测试代码
if __name__ == '__main__':
    root = tk.Tk()
    app = MainWindow(root)
    app.run()
