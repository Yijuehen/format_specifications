# Format Specifications 项目

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue?style=for-the-badge&logo=version&color=blue" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-lightgrey?style=for-the-badge&logo=linux&color=lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/Language-Python-yellow?style=for-the-badge&logo=python&color=yellow" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge&logo=license&color=green" alt="License">
</p>

## 项目简介

Format Specifications 是一个功能强大的浏览器自动化框架，专为现代Web应用测试和监控场景设计。该项目集成了基于Playwright的浏览器控制能力和自定义浏览器扩展的错误捕获功能，能够高效地处理各种复杂的浏览器自动化任务。项目采用模块化设计，具有良好的可扩展性和可维护性，适用于持续集成环境、自动化测试、数据抓取等多种应用场景。

<p align="center">
  <img src="./docs/images/project-overview.png" alt="项目概览" width="800">
</p>

## 核心特性

### 1. 智能浏览器管理

项目实现了自动化的Chromium浏览器启动和管理机制，支持多种浏览器启动方式的无缝切换。核心功能包括：

- **自动浏览器检测**：智能识别系统中已安装的Chromium浏览器，支持从环境变量、Playwright安装目录、系统路径等多个来源查找可用浏览器
- **远程调试支持**：通过Chrome DevTools Protocol (CDP) 实现浏览器的远程控制，支持端口9222的调试连接
- **浏览器单例管理**：自动处理浏览器实例锁文件，避免因残留锁文件导致的启动冲突
- **资源优化配置**：针对容器环境优化，禁用不必要的功能以降低资源消耗

```
┌─────────────────────────────────────────────────────────────┐
│                    浏览器启动流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌────────────┐  │
│   │  环境变量检测  │ -> │ Playwright   │ -> │ 系统浏览器  │  │
│   │  CHROMIUM_PATH│    │ Chromium     │    │ 搜索        │  │
│   └──────────────┘    └──────────────┘    └────────────┘  │
│          │                   │                   │          │
│          └───────────────────┴───────────────────┘          │
│                          │                                    │
│                          v                                    │
│                   ┌────────────┐                              │
│                   │  返回可执行  │                              │
│                   │  文件路径    │                              │
│                   └────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 错误捕获扩展

项目集成了自定义开发的Chrome浏览器扩展，专门用于监控和记录Web应用中的各类错误：

- **全URL覆盖**：支持监听所有网页的网络请求和错误事件
- **Supabase API监控**：专门优化了对Supabase服务的API调用监控，包括REST API、Edge Functions、Auth和Storage等
- **请求生命周期追踪**：完整记录每个网络请求的发起、响应头接收、完成或错误等各个阶段
- **详细日志记录**：记录请求方法、URL、请求体、响应状态、耗时等详细信息

```
┌─────────────────────────────────────────────────────────────┐
│                  错误捕获扩展架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  Manifest V3                        │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │   │
│   │  │  Background │  │   Content   │  │  Injector  │  │   │
│   │  │   Service   │  │   Scripts   │  │   Script   │  │   │
│   │  │   Worker    │  │             │  │            │  │   │
│   │  └─────────────┘  └─────────────┘  └────────────┘  │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │               WebRequest API                         │   │
│   │  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │   │
│   │  │ onBefore   │  │ onHeaders  │  │  onCompleted │  │   │
│   │  │ Request    │  │ Received   │  │  /Error       │  │   │
│   │  └────────────┘  └────────────┘  └──────────────┘  │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                   │
│                          v                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              日志处理与转发                            │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. 容器环境优化

针对在Docker容器中运行的特殊需求，项目进行了多项针对性优化：

- 禁用沙箱模式（--no-sandbox）以适应容器环境
- 禁用共享内存使用（--disable-dev-shm-usage）避免内存不足问题
- 禁用GPU加速减少资源占用
- 自动化检测和连接已运行的Chrome实例
- 智能等待机制确保浏览器完全启动后再进行操作

## 项目架构

整体项目采用分层架构设计，各组件职责清晰、耦合度低，便于扩展和维护：

```
┌─────────────────────────────────────────────────────────────┐
│                      项目架构图                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   应用层                              │   │
│   │   ┌─────────────────────────────────────────────┐   │   │
│   │   │          global_browser.py                   │   │   │
│   │   │    (浏览器启动与管理主模块)                     │   │   │
│   │   └─────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   扩展层                              │   │
│   │   ┌─────────────────────────────────────────────┐   │   │
│   │   │           error_capture 扩展                │   │   │
│   │   │  ┌─────────┐ ┌─────────┐ ┌─────────────┐  │   │   │
│   │   │  │background│ │ content │ │  injector   │  │   │   │
│   │   │  │  .js    │ │  .js    │ │    .js      │  │   │   │
│   │   │  └─────────┘ └─────────┘ └─────────────┘  │   │   │
│   │   └─────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   依赖层                              │   │
│   │   ┌──────────────┐  ┌──────────────┐                │   │
│   │   │   Playwright │  │   Chrome     │                │   │
│   │   │    (Python)  │  │   (浏览器)   │                │   │
│   │   └──────────────┘  └──────────────┘                │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 目录结构

以下是项目的完整目录结构：

```
format_specifications/
│
├── browser/                           # 浏览器相关模块
│   ├── global_browser.py              # 全局浏览器管理主模块
│   │
│   └── browser_extension/            # 浏览器扩展目录
│       └── error_capture/             # 错误捕获扩展
│           ├── manifest.json          # 扩展配置文件
│           ├── background.js          # 后台服务脚本
│           ├── content.js             # 内容脚本
│           └── injector.js            # 注入脚本
│
├── docs/                              # 文档目录
│   └── images/                        # 文档图片目录
│
└── README.md                          # 项目说明文件
```

## 快速开始

### 环境要求

在开始使用之前，请确保您的系统满足以下要求：

- **操作系统**：Linux (推荐 Ubuntu 20.04+ 或 CentOS 8+)
- **Python版本**：Python 3.8 或更高版本
- **浏览器**：Chromium (通过Playwright自动安装或系统已有)
- **依赖包**：aiohttp、playwright、neo-utils

### 安装步骤

按照以下步骤完成项目环境搭建：

**第一步：安装Python依赖**

```bash
pip install aiohttp playwright neo-utils
```

**第二步：安装Playwright浏览器**

```bash
python -m playwright install chromium
```

**第三步：配置环境变量（可选）**

如果您需要指定特定的Chromium浏览器路径，可以设置环境变量：

```bash
export CHROMIUM_PATH=/path/to/your/chromium
```

### 使用示例

以下是如何在您的项目中使用全局浏览器功能的代码示例：

```python
import asyncio
from browser.global_browser import launch_chrome_debug

async def main():
    """
    启动带调试功能的Chrome浏览器
    """
    try:
        # 启动浏览器（headless模式可选）
        await launch_chrome_debug(headless=False)
        print("浏览器启动成功！")
    except Exception as e:
        print(f"启动失败: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 高级配置

**自定义浏览器启动参数**

您可以通过修改`chrome_args`列表来添加或修改启动参数：

```python
chrome_args = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-blink-features=AutomationControlled",
    # 添加自定义参数
    "--window-size=1920,1080",
    "--lang=zh-CN",
]
```

**配置远程调试端口**

项目默认使用9222端口进行远程调试，您可以通过修改代码来更改端口：

```python
"--remote-debugging-port=9222",  # 修改此值以更改端口
```

## API 监控功能

错误捕获扩展专门针对Supabase服务进行了优化，能够监控以下类型的API请求：

| API类型 | 监控范围 | 记录内容 |
|---------|----------|----------|
| REST API | `*.supabase.co/rest/*` | 完整请求/响应信息 |
| Edge Functions | `*.supabase.co/functions/*` | 函数调用详情 |
| Auth | `*.supabase.co/auth/*` | 认证请求信息 |
| Storage | `*.supabase.co/storage/*` | 存储操作记录 |

扩展会记录以下关键信息：

- 请求方法和URL
- 请求头和请求体
- 响应状态码和响应头
- 请求耗时
- 错误信息（如果有）

## 常见问题

### Q1: 启动浏览器时提示"未找到Chromium浏览器"

**解决方案**：
1. 确保已运行 `python -m playwright install chromium`
2. 或设置环境变量 `CHROMIUM_PATH` 指向您的Chromium可执行文件

### Q2: 浏览器启动后立即退出

**解决方案**：
1. 检查是否有其他Chrome实例正在运行
2. 删除 `/workspace/browser/user_data/` 目录下的锁文件
3. 确保容器有足够的内存资源

### Q3: 无法连接到已运行的Chrome实例

**解决方案**：
1. 确认Chrome的远程调试端口（默认9222）未被占用
2. 检查防火墙设置是否阻止本地连接
3. 查看Chrome启动日志排查具体错误

## 性能考量

为了获得最佳性能，建议在配置较低的资源环境下运行时注意以下事项：

- **内存限制**：容器建议分配至少2GB内存
- **CPU资源**：建议至少分配2个CPU核心
- **浏览器上下文**：根据需要创建，避免同时打开过多标签页
- **等待时间**：根据网络状况调整浏览器启动等待时间

## 贡献指南

欢迎对项目进行贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

## 许可证

本项目基于 MIT 许可证开源，详情请参见 [LICENSE](LICENSE) 文件。

---

<p align="center">
  <img src="https://img.shields.io/badge/Made-with-Python-blue?style=for-the-badge&logo=python" alt="Made with Python">
  <img src="https://img.shields.io/badge/Powered_by-Playwright-green?style=for-the-badge&logo=playwright" alt="Powered by Playwright">
</p>

<p align="center">
  © 2024 Format Specifications. All rights reserved.
</p>
