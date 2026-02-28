# OpenClaw 简易安装器 v2.0

## 📌 为什么做这个版本？

**之前的版本太复杂了：**
- ❌ PyInstaller 打包遇到各种问题（requests 模块等）
- ❌ 安装包太大（10-40 MB）
- ❌ 需要频繁修复打包问题
- ❌ 安装过程不透明

**新版本的优势：**
- ✅ **简单直接**：直接执行终端命令
- ✅ **不需要打包**：Python 脚本直接运行
- ✅ **安装过程透明**：终端可以看到所有输出
- ✅ **双模式支持**：GUI 模式 + 终端模式

---

## 🚀 快速开始

### 方法 1：下载并运行（推荐）

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/summercard/ocbananaInstaller/main/simple_installer.py

# 运行
python3 simple_installer.py
```

### 方法 2：直接运行

```bash
# 如果已克隆仓库
cd OpenClawInstaller
python3 simple_installer.py
```

---

## 📋 安装流程

### macOS 安装

**自动安装的内容：**
1. ✅ 检查并安装 Homebrew（包管理器）
2. ✅ 检查并安装 Node.js
3. ✅ 检查并安装 npm
4. ✅ 安装 OpenClaw（`npm install -g openclaw-cn`）
5. ✅ 验证安装

**时间：** 约 5-10 分钟（首次安装）

### Windows 安装

**需要手动安装：**
1. ⚠️ 访问 https://nodejs.org/ 下载并安装 Node.js
2. ✅ 安装程序会自动安装 npm
3. ✅ 安装 OpenClaw（`npm install -g openclaw-cn`）
4. ✅ 验证安装

**时间：** 约 2-3 分钟（Node.js 已安装的情况下）

---

## 🎯 两种模式

### GUI 模式

**适用场景：** 有 tkinter 支持的系统

**界面：**
- 标签页：macOS / Windows
- 安装按钮：一键安装
- 终端输出：实时显示安装过程

**优势：**
- ✅ 图形界面，简单易用
- ✅ 实时显示终端输出
- ✅ 可以看到完整的安装过程

### 终端模式

**适用场景：** 没有 tkinter 支持的系统

**界面：**
- 命令行菜单
- 选项 1：安装 OpenClaw
- 选项 2：退出

**优势：**
- ✅ 不需要 tkinter
- ✅ 更轻量
- ✅ 适合服务器环境

---

## 📖 使用示例

### 示例 1：macOS 安装（GUI 模式）

```bash
# 1. 运行安装器
python3 simple_installer.py

# 2. 界面会自动检测到 macOS
# 3. 点击"开始安装"按钮
# 4. 等待安装完成（查看终端输出）
```

### 示例 2：macOS 安装（终端模式）

```bash
# 1. 运行安装器
python3 simple_installer.py

# 2. 输入 1 选择安装
# 3. 等待安装完成
```

### 示例 3：Windows 安装

```bash
# 1. 先安装 Node.js（从 nodejs.org 下载）
# 2. 运行安装器
python simple_installer.py

# 3. 点击"开始安装"按钮（Windows 标签页）
# 4. 等待安装完成
```

---

## 🔍 与之前版本的对比

| 特性 | 之前版本（复杂） | 新版本（简单） |
|------|----------------|--------------|
| **打包方式** | PyInstaller 打包 | 不需要打包 |
| **安装包大小** | 10-40 MB | ~50 KB（脚本） |
| **依赖问题** | 需要手动添加 hidden-import | 不需要 |
| **安装过程** | 不透明（PyInstaller 打包） | 透明（终端输出） |
| **更新方式** | 重新打包 | 直接运行脚本 |
| **调试难度** | 困难（打包后看不到代码） | 简单（直接修改脚本） |
| **双平台支持** | 需要分别打包 | 一个脚本支持所有平台 |

---

## 🛠️ 安装后验证

### 验证安装

```bash
# macOS/Linux
openclaw-cn --version

# Windows
openclaw-cn --version
```

### 启动 OpenClaw

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

---

## ❓ 常见问题

### Q1: macOS 提示 tkinter 未安装怎么办？

**A:** 安装 tkinter：

```bash
brew install python-tk@3.11
```

或者使用终端模式（不需要 tkinter）

### Q2: Windows 提示 Node.js 未安装怎么办？

**A:** 访问 https://nodejs.org/ 下载并安装 Node.js LTS 版本

### Q3: 安装速度慢怎么办？

**A:** 可能是网络原因，可以：
1. 等待一段时间（可能 10-20 分钟）
2. 配置 npm 使用国内镜像：
   ```bash
   npm config set registry https://registry.npmmirror.com
   ```

### Q4: 权限问题怎么办？

**A:**
- macOS/Linux：使用 `sudo`
  ```bash
  sudo npm install -g openclaw-cn
  ```
- Windows：以管理员身份运行

### Q5: 安装失败怎么办？

**A:** 查看终端输出的错误信息：
1. 检查网络连接
2. 检查磁盘空间（至少 500MB）
3. 重试安装

---

## 🎯 最佳实践

### 1. 首次安装建议

**macOS 用户：**
1. 确保有 Xcode Command Line Tools
2. 可以提前安装 Homebrew（可选，安装器会自动安装）

**Windows 用户：**
1. 提前安装 Node.js（从 nodejs.org）
2. 以管理员身份运行安装器

### 2. 定期更新

```bash
# 更新 OpenClaw
npm update -g openclaw-cn

# 验证版本
openclaw-cn --version
```

### 3. 卸载

```bash
# 卸载 OpenClaw
npm uninstall -g openclaw-cn

# （可选）卸载 Node.js 和 npm
# macOS: brew uninstall node npm
# Windows: 从控制面板卸载
```

---

## 📦 系统要求

### macOS

| 要求 | 版本 |
|------|------|
| 操作系统 | macOS 10.13+ |
| Python | 3.10+（运行安装器） |
| 磁盘空间 | 至少 500MB |
| 网络 | 需要访问互联网 |

### Windows

| 要求 | 版本 |
|------|------|
| 操作系统 | Windows 10+ |
| Python | 3.10+（运行安装器） |
| Node.js | 14+（安装器会提示） |
| 磁盘空间 | 至少 500MB |
| 网络 | 需要访问互联网 |

### Linux

| 要求 | 版本 |
|------|------|
| 操作系统 | 主流发行版（Ubuntu, Debian, CentOS 等）|
| Python | 3.10+（运行安装器） |
| Node.js | 14+（安装器会提示） |
| 磁盘空间 | 至少 500MB |
| 网络 | 需要访问互联网 |

---

## 🔧 故障排除

### 1. tkinter 导入错误

**错误信息：**
```
ModuleNotFoundError: No module named '_tkinter'
```

**解决方案：**
```bash
# macOS
brew install python-tk@3.11

# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

或使用终端模式（不需要 tkinter）

### 2. npm 命令未找到

**错误信息：**
```
npm: command not found
```

**解决方案：**
```bash
# macOS
brew install node

# Windows
访问 https://nodejs.org/ 下载安装
```

### 3. 权限拒绝

**错误信息：**
```
EACCES: permission denied
```

**解决方案：**
```bash
# macOS/Linux
sudo npm install -g openclaw-cn

# Windows
以管理员身份运行
```

### 4. 网络超时

**错误信息：**
```
ETIMEDOUT
```

**解决方案：**
```bash
# 使用国内镜像
npm config set registry https://registry.npmmirror.com

# 或使用代理
npm config set proxy http://your-proxy:port
```

---

## 📝 更新日志

### v2.0 (2026-02-28)

- ✅ 重新设计，使用简单直接的方法
- ✅ 移除 PyInstaller 打包
- ✅ 添加双模式支持（GUI + 终端）
- ✅ 自动检测平台
- ✅ 实时显示安装输出
- ✅ 支持所有平台（macOS, Windows, Linux）

### v1.0 (2026-02-27)

- ❌ 复杂的 PyInstaller 打包方案
- ❌ 遇到各种依赖问题
- ❌ 安装包太大

---

## 🎉 总结

**新版本的优势：**
1. ✅ 简单：直接执行终端命令，不需要复杂打包
2. ✅ 透明：所有安装过程都可见
3. ✅ 轻量：脚本只有 ~50 KB
4. ✅ 灵活：支持 GUI 和终端两种模式
5. ✅ 跨平台：一个脚本支持所有平台

**推荐使用方式：**
- macOS/Linux：直接运行脚本（终端模式）
- Windows：直接运行脚本（需要先安装 Node.js）

---

**文档版本：** v2.0
**最后更新：** 2026-02-28
**作者：** 杰西卡 🎀
