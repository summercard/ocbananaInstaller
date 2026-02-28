# OpenClawInstaller 安装指南

本指南详细说明如何在不同平台上安装和使用OpenClawInstaller。

## 目录

- [Windows安装](#windows安装)
- [macOS安装](#macos安装)
- [常见安装问题](#常见安装问题)
- [卸载说明](#卸载说明)

---

## Windows安装

### 方法一：使用可执行文件（推荐）

1. **下载**
   - 访问[发布页面](https://github.com/your-repo/OpenClawInstaller/releases)
   - 下载 `OpenClawInstaller.exe`

2. **运行**
   - 双击 `OpenClawInstaller.exe`
   - 如果提示"无法验证发布者"，点击"更多信息"→"仍要运行"

3. **安装OpenClaw**
   - 打开程序
   - 点击"开始安装"
   - 等待安装完成

### 方法二：从源码运行

1. **安装Python**
   - 访问 [Python官网](https://www.python.org/downloads/)
   - 下载Python 3.10或更高版本
   - 安装时勾选"Add Python to PATH"

2. **安装Node.js**
   - 访问 [Node.js官网](https://nodejs.org/)
   - 下载并安装LTS版本

3. **克隆项目**
   ```cmd
   git clone https://github.com/your-repo/OpenClawInstaller.git
   cd OpenClawInstaller
   ```

4. **安装依赖**
   ```cmd
   pip install -r requirements.txt
   ```

5. **运行程序**
   ```cmd
   python main.py
   ```

---

## macOS安装

### 方法一：使用可执行文件（推荐）

1. **下载**
   - 访问[发布页面](https://github.com/your-repo/OpenClawInstaller/releases)
   - 下载 `OpenClawInstaller`

2. **运行**
   - 双击 `OpenClawInstaller`
   - 如果提示"无法打开"，右键点击→"打开"

3. **安装OpenClaw**
   - 打开程序
   - 点击"开始安装"
   - 等待安装完成

### 方法二：从源码运行

1. **检查Python**
   ```bash
   python3 --version
   ```
   如果未安装或版本过低，使用Homebrew安装：
   ```bash
   brew install python@3.11
   ```

2. **安装Node.js**
   ```bash
   brew install node
   ```

3. **克隆项目**
   ```bash
   git clone https://github.com/your-repo/OpenClawInstaller.git
   cd OpenClawInstaller
   ```

4. **安装依赖**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **运行程序**
   ```bash
   python3 main.py
   ```

---

## 常见安装问题

### 问题1：Windows提示"无法验证发布者"

**解决方案：**
1. 点击"更多信息"
2. 点击"仍要运行"
3. 或者右键点击文件→属性→解除锁定

### 问题2：macOS提示"无法打开，因为无法验证开发者"

**解决方案：**
1. 打开"系统偏好设置"→"安全性与隐私"
2. 点击"仍要打开"
3. 或者在终端运行：
   ```bash
   xattr -cr OpenClawInstaller
   ```

### 问题3：提示"Python未安装"

**解决方案：**
- Windows：访问 https://www.python.org/downloads/ 下载安装
- macOS：运行 `brew install python` 或访问官网下载

### 问题4：提示"Node.js未安装"

**解决方案：**
- Windows/macOS：访问 https://nodejs.org/ 下载安装
- macOS：运行 `brew install node`

### 问题5：pip安装依赖失败

**解决方案：**
```bash
# 升级pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题6：磁盘空间不足

**解决方案：**
- 清理临时文件
- 删除不必要的程序
- 确保至少有500MB可用空间

### 问题7：网络连接问题

**解决方案：**
- 检查网络连接
- 配置代理（如果需要）
- 检查防火墙设置

---

## 卸载说明

### 卸载OpenClawInstaller

1. **删除可执行文件**
   - Windows：删除 `OpenClawInstaller.exe`
   - macOS：删除 `OpenClawInstaller` 应用程序

2. **删除配置文件**
   ```bash
   # Windows
   %APPDATA%\OpenClawInstaller\

   # macOS
   ~/Library/Application Support/OpenClawInstaller/
   ```

### 卸载OpenClaw

1. **使用OpenClawInstaller卸载**
   - 在终端运行：`npm uninstall -g openclaw-cn`

2. **或手动删除**
   - 删除安装目录
   - 删除配置文件

---

## 验证安装

安装完成后，运行以下命令验证：

```bash
# 检查Python
python --version

# 检查Node.js
node --version

# 检查OpenClaw
openclaw-cn --version
```

---

## 需要帮助？

如果遇到问题：
1. 查看[常见问题文档](FAQ.md)
2. 提交Issue：https://github.com/your-repo/OpenClawInstaller/issues
3. 联系开发者：your-email@example.com

---

*最后更新：2026年2月27日*
