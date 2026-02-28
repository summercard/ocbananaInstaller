# OpenClawInstaller

OpenClaw 跨平台安装工具 - 图形化安装管理界面

## 功能特性

- ✅ 环境自动检查（Python、Node.js、磁盘空间、网络）
- ✅ 一键安装 OpenClaw
- ✅ 配置管理（安装目录、端口、自动启动）
- ✅ 进程管理（启动/停止/重启）
- ✅ 状态监控
- ✅ 内置日志查看

## 下载安装

### 方式一：直接下载（推荐）

访问 [Releases](https://github.com/yourusername/openclawinstaller/releases) 页面，下载对应平台的安装包：

- Windows: `OpenClawInstaller-Windows-x64.exe`
- macOS: `OpenClawInstaller-macOS-x64.zip`
- Linux: `OpenClawInstaller-Linux-x64.tar.gz`

### 方式二：自行构建

```bash
# 克隆仓库
git clone https://github.com/yourusername/openclawinstaller.git
cd openclawinstaller/OpenClawInstaller

# 安装依赖
pip install pyinstaller

# 构建
pyinstaller --name=OpenClawInstaller --windowed --onefile main.py

# 可执行文件在 dist/ 目录
```

## 使用说明

### 安装 OpenClaw

1. 双击运行 `OpenClawInstaller`
2. 点击「安装」标签
3. 查看环境检查结果
4. 点击「开始安装」

### 配置 OpenClaw

1. 点击「配置」标签
2. 修改配置项（安装目录、端口号等）
3. 点击「保存配置」

### 管理服务

1. 点击「状态」标签
2. 查看当前运行状态
3. 使用按钮控制（启动/停止/打开 Web 界面）

## 系统要求

- Windows 10+ / macOS 10.13+ / Linux（主流发行版）
- **Python 3.10+**（如果自行构建）
- **Node.js 14+**（OpenClaw 依赖）
- 至少 500MB 可用磁盘空间
- 可访问 GitHub 的网络连接

## 开发

### 项目结构

```
OpenClawInstaller/
├── main.py              # 主入口
├── build.py             # 打包脚本
├── gui/                 # GUI 界面
│   └── main_window.py   # 主窗口
├── core/                # 核心功能
│   ├── installer.py     # 安装器
│   ├── manager.py       # 进程管理器
│   ├── env_checker.py   # 环境检查
│   └── config.py        # 配置管理
└── utils/               # 工具类
    ├── logger.py        # 日志
    ├── downloader.py    # 下载器
    └── platform.py      # 平台检测
```

### 运行开发版本

```bash
cd OpenClawInstaller
python main.py
```

### 本地构建

```bash
# 正式版本（无控制台）
python build.py

# 开发版本（带控制台）
python build.py --dev
```

## GitHub Actions 自动构建

本项目使用 GitHub Actions 自动构建多平台可执行文件：

### 触发构建

**方式一：发布标签**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**方式二：手动触发**
1. 访问 GitHub Actions 页面
2. 选择 "Build OpenClawInstaller"
3. 点击 "Run workflow"

### 下载构建产物

构建完成后，有两种方式下载：

**方式一：从 Release 下载**
- 访问 [Releases](https://github.com/yourusername/openclawinstaller/releases)
- 下载对应平台的文件

**方式二：从 Actions 下载**
- 访问 [Actions](https://github.com/yourusername/openclawinstaller/actions)
- 选择对应的 workflow 运行
- 在 "Artifacts" 部分下载

## 故障排除

### Windows 运行时被拦截

- 右键 → 属性 → 解除锁定
- 或在 Windows Defender 中添加信任

### macOS 运行时被拦截

```bash
# 移除隔离属性
xattr -cr OpenClawInstaller.app
```

### 环境检查失败

1. **Python 版本不足**
   - Windows: 访问 [python.org](https://www.python.org/downloads/)
   - macOS: `brew install python@3.11`
   - Linux: `sudo apt install python3.11`

2. **Node.js 未安装**
   - 访问 [nodejs.org](https://nodejs.org/) 下载安装

3. **网络连接失败**
   - 检查代理设置
   - 确保可以访问 GitHub

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 项目主页: [GitHub](https://github.com/yourusername/openclawinstaller)
- 问题反馈: [Issues](https://github.com/yourusername/openclawinstaller/issues)
