# OpenClaw 简易安装器

简单的 OpenClaw 安装器，通过 GUI 界面执行终端命令。

## 下载地址

[下载页面](https://github.com/summercard/ocbananaInstaller/releases)

## 使用方法

### Windows

1. 下载 `OpenClawInstaller-Windows-x64.exe`
2. 双击运行
3. 按顺序点击按钮：

   **第一阶段：安装基础环境**
   - **检查环境**：查看当前环境状态（Node.js、Git）
   - **安装 Node.js**：使用 winget 静默安装 Node.js LTS
   - **刷新环境变量**：安装 Node.js 后需手动关闭并重新打开 CMD
   - **安装 Git**：使用 winget 安装 Git

   **第二阶段：安装 OpenClaw 本体**
   - **安装 OpenClaw 核心**：使用 npm 全局安装
   - **测试安装**：验证 OpenClaw 版本

   **第三阶段：配置与启动**
   - **注册后台网关服务**：安装守护进程
   - **启动 Gateway**：启动本地网关服务
   - **进入控制台**：服务启停与 API 配置

### macOS

1. 下载 `OpenClawInstaller-macOS-x64.zip`
2. 解压缩
3. 双击运行
4. 按顺序点击按钮（同 Windows 步骤）

### Linux

1. 下载 `OpenClawInstaller-Linux-x64.tar.gz`
2. 解压缩：`tar xzf OpenClawInstaller-Linux-x64.tar.gz`
3. 运行：`./OpenClawInstaller`

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

### Windows
- Windows 10 或更高版本
- 至少 500MB 可用磁盘空间
- 可访问互联网

### macOS
- macOS 10.13 或更高版本
- 至少 500MB 可用磁盘空间
- 可访问互联网

### Linux
- 主流 Linux 发行版
- 至少 500MB 可用磁盘空间
- 可访问互联网

## 注意事项

- 安装过程需要联网
- 首次安装可能需要 5-10 分钟
- 如果 winget 不可用，Windows 用户可以手动从 https://nodejs.org/ 下载安装 Node.js
