# 系统架构逻辑图
# System Architecture Diagram

## 1. 整体架构图 (Overall Architecture)

```mermaid
graph TB
    subgraph "用户层 (User Layer)"
        User[用户<br/>User]
        Browser[Web浏览器<br/>Web Browser]
    end

    subgraph "前端展示层 (Frontend Layer)"
        UploadUI[文档上传界面<br/>Upload UI]
        TemplateUI[模板生成界面<br/>Template UI]
        SegmentationUI[文档分割界面<br/>Segmentation UI]
        DownloadUI[结果下载<br/>Download UI]
    end

    subgraph "Django后端层 (Backend Layer)"
        URLRouter[URL路由<br/>URL Router]
        UploadView[文档上传视图<br/>Upload View]
        TemplateView[模板生成视图<br/>Template View]
        SegmentationView[分割处理视图<br/>Segmentation View]
    end

    subgraph "业务逻辑层 (Business Logic Layer)"
        TemplateMgr[模板管理器<br/>Template Manager]
        AIProcessor[AI文本处理器<br/>AI Processor]
        WordFormatter[Word格式化器<br/>Word Formatter]
        ImageTracker[图片追踪器<br/>Image Tracker]
        DocExtractor[文档提取器<br/>Document Extractor]
    end

    subgraph "数据层 (Data Layer)"
        SQLite[(SQLite数据库<br/>Templates & Logs)]
        MediaFiles[媒体文件存储<br/>Media Storage]
        TempFiles[临时文件<br/>Temp Files]
    end

    subgraph "外部服务层 (External Services)"
        ZhipuAI[智谱AI GLM模型<br/>Zhipu AI API]
        DocxLib[python-docx库<br/>Word Processing]
    end

    User --> Browser
    Browser --> UploadUI
    Browser --> TemplateUI
    Browser --> SegmentationUI

    UploadUI --> URLRouter
    TemplateUI --> URLRouter
    SegmentationUI --> URLRouter

    URLRouter --> UploadView
    URLRouter --> TemplateView
    URLRouter --> SegmentationView

    UploadView --> TemplateMgr
    UploadView --> AIProcessor
    UploadView --> WordFormatter
    UploadView --> ImageTracker

    TemplateView --> TemplateMgr
    TemplateView --> AIProcessor
    TemplateView --> DocExtractor
    TemplateView --> WordFormatter

    SegmentationView --> DocExtractor

    AIProcessor --> ZhipuAI
    WordFormatter --> DocxLib
    ImageTracker --> DocxLib

    TemplateMgr --> SQLite
    TemplateMgr --> MediaFiles
    UploadView --> TempFiles
    WordFormatter --> TempFiles

    DownloadUI --> MediaFiles
    Browser --> DownloadUI

    style User fill:#e1f5fe
    style ZhipuAI fill:#fff3e0
    style SQLite fill:#f3e5f5
```

## 2. 数据流图 (Data Flow Diagram)

```mermaid
sequenceDiagram
    participant U as 用户 User
    participant UI as 前端界面 UI
    participant V as Django视图 View
    participant TM as 模板管理器 TemplateManager
    participant AI as AI处理器 AIProcessor
    participant WF as Word格式化器 WordFormatter
    participant IT as 图片追踪器 ImageTracker
    participant DB as 数据库 Database
    participant ZAI as 智谱AI ZhipuAI

    U->>UI: 上传Word文档
    UI->>V: POST /upload-word-ai/
    V->>V: 验证文件格式

    alt 简单模式 Simple Mode
        V->>WF: 提取文档内容
        WF->>IT: 提取图片
        IT-->>WF: 返回图片映射
        WF->>AI: AI文本优化
        AI->>ZAI: 调用GLM模型
        ZAI-->>AI: 返回优化文本
        AI-->>WF: 返回处理结果
        WF->>WF: 重新插入图片
        WF->>WF: 应用样式模板
        WF-->>V: 返回格式化文档
    else 模板模式 Template Mode
        V->>TM: 获取模板结构
        TM->>DB: 查询模板
        DB-->>TM: 返回模板数据
        TM-->>V: 返回模板结构
        V->>AI: 根据模板生成内容
        AI->>ZAI: 调用GLM模型
        ZAI-->>AI: 返回生成内容
        AI-->>V: 返回结构化内容
        V->>WF: 创建Word文档
        WF-->>V: 返回生成文档
    else 自定义模式 Custom Mode
        V->>AI: 根据用户结构生成
        AI->>ZAI: 调用GLM模型
        ZAI-->>AI: 返回生成内容
        V->>WF: 创建Word文档
        WF-->>V: 返回生成文档
    end

    V->>TM: 记录使用日志
    TM->>DB: 保存日志
    V-->>UI: 返回文档下载链接
    UI-->>U: 下载处理后的文档
```

## 3. 核心模块架构图 (Core Module Architecture)

```mermaid
graph LR
    subgraph "模板管理模块 (Template Management)"
        TM1[预定义模板<br/>Predefined Templates]
        TM2[用户自定义模板<br/>Custom Templates]
        TM3[模板CRUD操作<br/>CRUD Operations]
        TM4[使用统计<br/>Usage Analytics]
    end

    subgraph "AI处理模块 (AI Processing Module)"
        AI1[文本优化<br/>Text Enhancement]
        AI2[内容生成<br/>Content Generation]
        AI3[语气风格<br/>Tone Styles]
        AI4[缓存机制<br/>Cache System]
        AI5[重试逻辑<br/>Retry Logic]
    end

    subgraph "文档处理模块 (Document Processing Module)"
        DP1[文本提取<br/>Text Extraction]
        DP2[图片处理<br/>Image Processing]
        DP3[样式应用<br/>Style Application]
        DP4[结构化输出<br/>Structured Output]
    end

    subgraph "图片追踪模块 (Image Tracking Module)"
        IT1[图片提取<br/>Image Extraction]
        IT2[语义匹配<br/>Semantic Matching]
        IT3[位置映射<br/>Position Mapping]
        IT4[智能重插入<br/>Smart Reinsertion]
    end

    TM1 --> TM3
    TM2 --> TM3
    TM3 --> TM4

    AI1 --> AI4
    AI2 --> AI4
    AI3 --> AI4
    AI4 --> AI5

    DP1 --> DP3
    DP2 --> DP3
    DP3 --> DP4

    IT1 --> IT2
    IT2 --> IT3
    IT3 --> IT4
```

## 4. 数据库模型关系图 (Database Schema)

```mermaid
erDiagram
    DOCUMENT_TEMPLATE ||--o{ TEMPLATE_USAGE_LOG : "has many"

    DOCUMENT_TEMPLATE {
        integer id PK
        string template_id UK "模板唯一标识"
        string name "模板名称"
        string description "模板描述"
        string category "模板分类"
        json sections_json "章节结构JSON"
        string template_type "模板类型"
        string created_by "创建者"
        string version "版本号"
        integer usage_count "使用次数"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    TEMPLATE_USAGE_LOG {
        integer id PK
        integer user_id FK "用户ID"
        integer template_id FK "模板ID"
        text user_outline "用户大纲"
        boolean had_source_document "是否有源文档"
        boolean generation_success "生成是否成功"
        float generation_duration "生成耗时(秒)"
        datetime created_at "创建时间"
    }

    USER {
        integer id PK
        string username UK "用户名"
        string email "邮箱"
        datetime created_at "创建时间"
    }
```

## 5. 部署架构图 (Deployment Architecture)

```mermaid
graph TB
    subgraph "客户端 (Client Side)"
        Browser[Chrome/Edge/Firefox]
    end

    subgraph "Web服务器 (Web Server)"
        Nginx[Nginx<br/>静态文件服务 & 反向代理]
    end

    subgraph "应用服务器 (Application Server)"
        Gunicorn[Gunicorn<br/>WSGI服务器]
        Django[Django应用<br/>Format Specifications]
    end

    subgraph "数据存储 (Data Storage)"
        SQLite[(SQLite<br/>数据库)]
        Media[媒体文件目录<br/>Media/]
        Temp[临时文件目录<br/>Tmp/]
    end

    subgraph "外部API (External APIs)"
        Zhipu[智谱AI API<br/>Zhipu AI GLM-4]
    end

    Browser -->|HTTP/HTTPS| Nginx
    Nginx -->|静态文件| Browser
    Nginx -->|反向代理| Gunicorn
    Gunicorn --> Django

    Django --> SQLite
    Django --> Media
    Django --> Temp
    Django -->|HTTPS API调用| Zhipu

    style Browser fill:#e3f2fd
    style Zhipu fill:#fff3e0
    style SQLite fill:#f3e5f5
```

## 6. 功能模块详细说明 (Module Details)

### 6.1 前端模块 (Frontend Module)

| 模块 | 功能 | 文件 |
|------|------|------|
| 文档上传 | 支持拖拽上传,文件验证 | upload_word_ai.html |
| 模板选择 | 展示10种预定义模板 | template_generation.html |
| 配置面板 | 样式选择,语气调整 | settings.html |
| 进度显示 | 实时显示处理进度 | progress.js |
| 结果下载 | 支持中文文件名 | download.js |

### 6.2 后端服务模块 (Backend Services)

| 服务 | 职责 | 主要类/函数 |
|------|------|------------|
| 模板管理 | 模板CRUD,缓存 | TemplateManager |
| AI处理 | 文本生成,优化 | AIWordUtils |
| 文档格式化 | Word文档处理 | WordFormatter |
| 图片追踪 | 图片提取和重插入 | ImageTracker |
| 文档提取 | 内容提取和分析 | DocumentExtractor |

### 6.3 预定义模板列表 (Predefined Templates)

1. 年度工作总结 (Annual Work Summary)
2. 项目总结报告 (Project Summary Report)
3. 会议纪要 (Meeting Minutes)
4. 工作计划 (Work Plan)
5. 周报/月报 (Weekly/Monthly Report)
6. 调研报告 (Research Report)
7. 问题分析报告 (Problem Analysis Report)
8. 培训总结 (Training Summary)
9. 活动策划 (Event Planning)
10. 竞品分析 (Competitor Analysis)

### 6.4 AI功能特性 (AI Features)

- **多种语气风格**: 直接(Direct), 严谨(Rigorous), 共情(Empathetic), 专业(Professional)
- **智能缓存**: 避免重复API调用,降低成本
- **重试机制**: 指数退避重试,提高可靠性
- **超时控制**: 可配置的请求超时时间
- **错误处理**: 优雅降级,用户友好的错误提示

### 6.5 文档处理能力 (Document Processing Capabilities)

- **格式支持**: Microsoft Word (.docx)
- **图片处理**: 提取、语义匹配、智能重插入
- **样式模板**: 公文、学术、商务、休闲等多种风格
- **文本分割**: 段落、句子、语义单元三种模式
- **元数据保留**: 保存文档结构、格式信息

## 7. 技术栈 (Technology Stack)

### 前端技术 (Frontend)
- HTML5/CSS3
- Vanilla JavaScript
- Bootstrap (可选)
- jQuery (可选)

### 后端技术 (Backend)
- Python 3.x
- Django 6.0
- WSGI: Gunicorn

### 数据库 (Database)
- SQLite (开发环境)
- PostgreSQL/MySQL (生产环境推荐)

### 核心库 (Core Libraries)
- python-docx: Word文档处理
- httpx: HTTP客户端
- pydantic: 数据验证
- pillow: 图像处理

### AI服务 (AI Services)
- 智谱AI GLM-4 模型
- 自定义SDK集成

## 8. 性能优化策略 (Performance Optimization)

1. **AI缓存机制**: 相同内容不重复调用API
2. **异步处理**: 长时间任务异步执行
3. **临时文件管理**: 及时清理临时文件
4. **数据库索引**: 模板查询优化
5. **静态资源**: CDN加速(可选)
6. **连接池**: HTTP客户端连接复用

## 9. 安全性考虑 (Security Considerations)

1. **文件上传验证**: 文件类型、大小限制
2. **API密钥保护**: 环境变量存储
3. **SQL注入防护**: Django ORM参数化查询
4. **XSS防护**: 模板自动转义
5. **CSRF保护**: Django内置CSRF中间件
6. **错误日志**: 敏感信息不暴露给用户

---

**文档版本**: 1.0
**最后更新**: 2026-01-20
**维护者**: Format Specifications Team
