# LeafAuto 项目开发文档
2024年11月8日19:11:05

## 项目概述

LeafAuto 是一个基于 PyQt6 的桌面应用程序，旨在提供自动化任务处理和助手功能。项目包含多个模块，支持多种功能，如自动化信息处理、AI 助手、活动管理等。

## 文件结构

## 技术栈

### 1. **Python**
- **版本**: 3.11
- **用途**: 主要编程语言，用于开发整个应用程序。

### 2. **PyQt6**
- **版本**: 6.4.2
- **用途**: GUI 开发框架，用于创建用户界面。

### 3. **PyInstaller**
- **版本**: 5.6.2
- **用途**: 用于打包 Python 应用程序，生成可执行文件。

### 4. **requests**
- **版本**: 2.32.3
- **用途**: HTTP 请求库，用于与外部 API 进行通信。

### 5. **pywin32**
- **版本**: 308
- **用途**: Windows 平台上的扩展库，用于创建和管理互斥锁。

### 6. **QSharedMemory**
- **用途**: Qt 提供的进程间共享内存类，用于确保应用程序只有一个实例在运行。

## 模块介绍

### 1. `App.py`
- **描述**: 主程序入口文件，负责启动应用程序。
- **主要功能**:
  - 初始化 `QApplication`。
  - 检查是否有其他实例在运行。
  - 创建并显示主窗口。
  - 运行主事件循环。

### 2. `MainWindow.py`
- **描述**: 主窗口的 UI 文件，由 `Ui_MainWindow.py` 生成。
- **主要功能**:
  - 显示主界面。
  - 处理用户交互。

### 3. `ActivitiesWindow.py`
- **描述**: 活动窗口的 UI 文件，由 `Ui_Activities.py` 生成。
- **主要功能**:
  - 显示活动列表。
  - 处理活动相关的用户交互。

### 4. `AiAssistant.py`
- **描述**: AI 助手模块，提供智能助手功能。
- **主要功能**:
  - 调用 AI API 进行对话。
  - 处理 AI 返回的结果。

### 5. `Autolnfo.py`
- **描述**: 自动化信息处理模块。
- **主要功能**:
  - 处理和解析信息。
  - 执行自动化任务。

### 6. `common.py`
- **描述**: 公共工具函数模块。
- **主要功能**:
  - 日志记录。
  - 辅助函数。

### 7. `LeafAuto_version_info.txt`
- **描述**: 版本信息文件，用于 PyInstaller 生成版本信息。

### 8. `LeafProcess.py`
- **描述**: 进程管理模块。
- **主要功能**:
  - 管理后台进程。
  - 处理进程间的通信。

### 9. `split.py`
- **描述**: 分割处理模块。
- **主要功能**:
  - 分割大文件。
  - 处理分割后的文件。

### 10. `SystemInfo.py`
- **描述**: 系统信息模块。
- **主要功能**:
  - 获取系统信息。
  - 显示系统状态。

### 11. `Thread.py`
- **描述**: 线程管理模块。
- **主要功能**:
  - 创建和管理多线程。
  - 处理异步任务。

### 12. `update.py`
- **描述**: 更新模块。
- **主要功能**:
  - 检查更新。
  - 下载并安装更新。

### 13. `Ui_Activities.py` 和 `Ui_MainWindow.py`
- **描述**: 由 Qt Designer 生成的 UI 文件。
- **主要功能**:
  - 定义 UI 布局。
  - 提供 UI 元素的访问接口。

### 14. `QT_Ui/Activities.ui` 和 `QT_Ui/MainWindow.ui`
- **描述**: Qt Designer 设计的 UI 文件。
- **主要功能**:
  - 定义 UI 布局。
  - 通过 `pyuic6` 转换为 Python 代码。

## 运行原理

### 1. **单实例运行**
- **原理**: 使用 `QSharedMemory` 类来确保应用程序只有一个实例在运行。
- **实现**:
  - 在 `App.py` 中创建一个 `QSharedMemory` 对象。
  - 尝试附加到已存在的共享内存，如果成功则显示警告消息并退出。
  - 尝试创建共享内存，如果失败则显示错误消息并退出。

### 2. **UI 设计**
- **原理**: 使用 Qt Designer 设计 UI，然后通过 `pyuic6` 工具将 `.ui` 文件转换为 Python 代码。
- **实现**:
  - 设计 `MainWindow.ui` 和 `Activities.ui` 文件。
  - 使用 `pyuic6` 将 `.ui` 文件转换为 `Ui_MainWindow.py` 和 `Ui_Activities.py`。

### 3. **多线程处理**
- **原理**: 使用 `QThread` 类来创建和管理多线程，确保 UI 界面的响应性。
- **实现**:
  - 在 `Thread.py` 中定义多个线程类。
  - 在主窗口中启动和管理这些线程。

### 4. **AI 助手**
- **原理**: 使用外部 AI API 进行对话处理。
- **实现**:
  - 在 `AiAssistant.py` 中调用 AI API。
  - 处理 AI 返回的结果并显示在界面上。

## 依赖库

- **PyQt6**: 6.4.2
- **PyQt6-Qt**: 6.0.1
- **PyQt6-Qt6**: 6.4.2
- **PyQt6_sip**: 13.8.0
- **WMI**: 1.5.1
- **altgraph**: 0.17.4
- **beautifulsoup4**: 4.12.3
- **certifi**: 2024.8.30
- **charset-normalizer**: 3.4.0
- **click**: 8.1.7
- **colorama**: 0.4.6
- **comtypes**: 1.4.8
- **idna**: 3.10
- **packaging**: 24.1
- **pefile**: 2024.8.26
- **pillow**: 11.0.0
- **pip**: 24.3.1
- **psutil**: 6.1.0
- **pyinstaller**: 5.6.2
- **pyinstaller-hooks-contrib**: 2024.9
- **pyperclip**: 1.9.0
- **pyqt6-plugins**: 6.4.2.2.3
- **pyqt6-tools**: 6.4.2.3.3
- **python-dotenv**: 1.0.1
- **pywin32**: 308
- **pywin32-ctypes**: 0.2.3
- **qt6-applications**: 6.4.3.2.3
- **qt6-tools**: 6.4.3.1.3
- **requests**: 2.32.3
- **setuptools**: 75.3.0
- **soupsieve**: 2.6
- **typing_extensions**: 4.12.2
- **urllib3**: 2.2.3
- **wheel**: 0.44.0
- **wxauto**: 3.9.11.17.5