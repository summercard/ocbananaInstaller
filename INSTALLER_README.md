# OpenClaw 简易安装器 v2.1

## 📦 下载地址

**Windows 版本（.exe 启动器）：**
```
https://github.com/summercard/ocbananaInstaller/releases/download/v2.1.0/launcher.exe
```

**源代码（Python 脚本）：**
```
https://raw.githubusercontent.com/summercard/ocbananaInstaller/simple-installer-v2.1/simple_installer.py
```

## 🚀 使用方法

### Windows 用户

**方法 1：使用 .exe 启动器（推荐）**

1. 下载 `launcher.exe`
2. 双击运行
3. 界面会自动打开，选择 Windows 标签
4. 点击"开始安装"
5. 按步骤执行：
   - 步骤 1/3：检查依赖环境
   - 步骤 2/3：安装依赖环境（需要手动安装 Node.js）
   - 步骤 3/3：安装 OpenClaw

**方法 2：使用 Python 脚本**

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/summercard/ocbananaInstaller/simple-installer-v2.1/simple_installer.py

# 运行
python simple_installer.py
```

### macOS 用户

```bash
# 下载脚本
curl -O https://raw.githubusercontent.com/summercard/ocbananaInstaller/simple-installer-v2.1/simple_installer.py

# 运行
python3 simple_installer.py
```

## 📋 安装步骤

### Windows 安装步骤

**步骤 1/3：检查依赖环境**
- 检查 Node.js 是否安装
- 检查 npm 是否安装

**步骤 2/3：安装依赖环境**
- 提示用户访问 https://nodejs.org/ 下载并安装 Node.js
- Node.js 安装完成后，npm 会自动安装

**步骤 3/3：安装 OpenClaw**
- 运行 `npm install -g openclaw-cn`
- 验证安装

### macOS 安装步骤

**步骤 1/3：检查依赖环境**
- 检查系统版本
- 检查 Homebrew 是否安装
- 检查 Node.js 是否安装
- 检查 npm 是否安装
- 检查磁盘空间

**步骤 2/3：安装依赖环境**
- 安装 Homebrew（如果没有）
- 安装 Node.js（如果没有）
- 安装 npm（如果没有）

**步骤 3/3：安装 OpenClaw**
- 运行 `npm install -g openclaw-cn`
- 验证安装

## 🎯 版本特性

### v2.1 (当前版本)

- ✅ 分步骤安装（检查 → 安装依赖 → 安装 OpenClaw）
- ✅ 实时显示终端输出
- ✅ Windows .exe 启动器（简单启动）
- ✅ 支持 GUI 和终端双模式
- ✅ 跨平台支持

## ❓ 常见问题

### Q: Windows 提示需要安装 Node.js？

A: 访问 https://nodejs.org/ 下载并安装 Node.js LTS 版本，然后重新运行安装器。

### Q: macOS 安装失败？

A: 查看终端输出的错误信息，常见问题：
- 网络连接问题：检查网络
- 权限问题：使用 `sudo` 运行
- 磁盘空间不足：确保至少 500MB 可用空间

## 📖 文档

详细文档：[SIMPLE_INSTALLER_README.md](SIMPLE_INSTALLER_README.md)
