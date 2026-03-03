# OPENCLAW 邪修安装器

简单易用的 OpenClaw 安装器，通过 GUI 界面一键安装配置。

## 核心特性

- 🎀 **杰西卡陪伴** - 左侧动漫风格女孩陪伴安装过程
- ⚡ **一键安装** - 界面化操作，无需手动输入命令
- 🔮 **邪修模式** - 支持 Claude Code 安装法，更高效
- 🤖 **让 Claude 做** - 预设任务按钮，一键让 AI 帮你操作
- 🌐 **Token 自动匹配** - 自动读取配置文件中的 Gateway Token

## 下载地址

[下载页面](https://github.com/summercard/ocbananaInstaller/releases)

## 界面介绍

### 主界面

- **左侧**：杰西卡动漫形象陪伴
- **中间**：安装 OpenClaw 核心 + 邪修 Claude Code 安装法
- **右侧**：控制台入口 + 疑难解答

### 控制台界面

- **服务控制**：启动/停止 Gateway、查看状态、打开 Web UI
- **让 Claude Code 做**：预设 4 个常用任务，点击自动调用 Claude

## 使用方法

### macOS

1. 下载 `OpenClawInstaller-macOS-arm64.zip`
2. 解压缩
3. 双击运行 `OpenClawInstaller.app`

### Windows

1. 下载 `OpenClawInstaller-Windows-x64.exe`
2. 双击运行

### Linux

1. 下载 `OpenClawInstaller-Linux-x64.tar.gz`
2. 解压缩：`tar xzf OpenClawInstaller-Linux-x64.tar.gz`
3. 运行：`./OpenClawInstaller`

## 安装步骤

### 方式一：传统安装

1. **检查环境** - 查看 Node.js、Git 状态
2. **安装 Node.js** - 自动安装 LTS 版本
3. **安装 Git** - 版本控制工具
4. **安装 OpenClaw 核心** - npm 全局安装
5. **测试安装** - 验证版本

### 方式二：邪修 Claude Code 安装法（推荐）

1. 安装 Node.js（必须）
2. 点击"🔮 邪修：Claude Code安装法"
3. 步骤1：安装 Claude Code
4. 步骤2：安装 cc-switch（Mac）/ 下载 cc-switch（Windows）
5. 步骤3：打开 Claude，输入任务

## 控制台功能

### 让 Claude Code 做

预设任务按钮：
- 帮我安装 openclaw
- 检查 openclaw 代码
- 帮我安装 openclaw 飞书插件
- 帮我清理 openclaw 进程

点击按钮会自动：
1. 打开 Terminal/CMD
2. 启动 Claude Code
3. 复制任务到剪贴板（粘贴即可）

### 服务控制

- **启动服务** - 启动 Gateway
- **停止服务** - 停止 Gateway
- **查看状态** - 刷新指示灯
- **打开 Web UI** - 浏览器访问控制台

## 安装后使用

```bash
# 启动服务
openclaw-cn gateway start

# 停止服务
openclaw-cn gateway stop

# 查看状态
openclaw-cn gateway status

# 查看帮助
openclaw-cn --help
```

## 系统要求

- Node.js 18+ 
- macOS / Windows / Linux
- 至少 500MB 可用磁盘空间
- 可访问互联网

## 注意事项

- 安装过程需要联网
- 首次安装可能需要 5-10 分钟
- Windows 用户建议使用管理员权限运行
- macOS 用户可能需要授权终端权限
