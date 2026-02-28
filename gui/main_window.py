"""
主窗口
OpenClawInstaller的主界面
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional
from utils.logger import get_logger

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
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # 窗口居中
        self._center_window()

        # 禁止调整大小（可选）
        # self.root.resizable(False, False)

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
        # 主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 顶部导航栏
        self.nav_frame = ttk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, pady=(0, 10))

        # 内容区域
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 底部日志区域
        self.log_frame = ttk.LabelFrame(self.main_frame, text="日志输出")
        self.log_frame.pack(fill=tk.X, pady=(10, 0))

        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(
            self.log_frame,
            height=8,
            wrap=tk.WORD,
            state='disabled'
        )
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

        # 创建导航按钮
        self._create_navigation()

    def _create_navigation(self):
        """创建导航按钮"""
        # 导航按钮配置
        nav_buttons = [
            ("安装", "install", lambda: self._show_page("install")),
            ("配置", "config", lambda: self._show_page("config")),
            ("状态", "status", lambda: self._show_page("status"))
        ]

        self.nav_buttons = {}

        # 创建按钮
        for i, (text, name, command) in enumerate(nav_buttons):
            btn = ttk.Button(
                self.nav_frame,
                text=text,
                command=command,
                width=15
            )
            btn.pack(side=tk.LEFT, padx=(0, 5))

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

    def _create_install_page(self) -> ttk.Frame:
        """创建安装页面"""
        frame = ttk.Frame(self.content_frame)

        # 标题
        title_label = ttk.Label(
            frame,
            text="OpenClaw安装",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # 环境检查结果区域
        env_frame = ttk.LabelFrame(frame, text="环境检查")
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

        configs = [
            ("安装目录", "install_dir"),
            ("端口号", "port"),
            ("自动启动", "auto_start")
        ]

        for i, (label_text, key) in enumerate(configs):
            row_frame = ttk.Frame(config_frame)
            row_frame.pack(fill=tk.X, padx=10, pady=5)

            label = ttk.Label(row_frame, text=label_text, width=15)
            label.pack(side=tk.LEFT, padx=(0, 10))

            if key == "auto_start":
                # 复选框
                var = tk.BooleanVar()
                check = ttk.Checkbutton(row_frame, variable=var)
                check.pack(side=tk.LEFT)
                self.config_vars[key] = var
            else:
                # 输入框
                var = tk.StringVar()
                entry = ttk.Entry(row_frame, textvariable=var, width=30)
                entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
                self.config_vars[key] = var

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

    def _save_config(self):
        """保存配置"""
        self.logger.info("保存配置...")
        self._log_message("配置已保存")

        # TODO: 实现配置保存逻辑

    def _load_config(self):
        """加载配置"""
        self.logger.info("加载配置...")
        self._log_message("配置已加载")

        # TODO: 实现配置加载逻辑

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
