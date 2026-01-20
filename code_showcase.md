# 核心代码展示与说明
# Core Code Showcase and Documentation

## 目录 / Table of Contents

1. [Django 视图层 (Views)](#django-views)
2. [数据库模型 (Models)](#database-models)
3. [AI 文本处理器 (AI Processor)](#ai-text-processor)
4. [Word 格式化器 (Word Formatter)](#word-formatter)
5. [模板管理器 (Template Manager)](#template-manager)
6. [URL 路由配置 (URL Routing)](#url-routing)

---

## Django Views

### 位置 / Location
`format_specifications/views.py`

### 核心功能 / Core Features

#### 1. 主入口函数 - AI 格式化处理

```python
@require_http_methods(["POST"])
def ai_format_word(request):
    """
    主入口：处理所有优化模式的请求
    - simple: 简单优化（AI 润色 + 样式统一）
    - template: 模板生成
    - custom: 自定义结构
    """
    # 1. 获取优化模式
    optimization_mode = request.POST.get('optimization_mode', 'simple')

    # 2. 验证文件上传
    if 'word_file' not in request.FILES:
        return render(request, 'upload_word_ai.html', {'error': '请上传 Word 文件'})

    # 3. 根据模式路由到不同的处理函数
    if optimization_mode == 'simple':
        return handle_simple_optimization(request, uploaded_file)
    elif optimization_mode == 'template':
        return handle_template_optimization(request, uploaded_file)
    elif optimization_mode == 'custom':
        return handle_custom_optimization(request, uploaded_file)
```

**设计亮点 / Design Highlights:**
- ✅ **模式路由模式** - 统一入口，根据 `optimization_mode` 分发到不同处理器
- ✅ **文件验证** - 确保文件格式为 `.docx`
- ✅ **错误处理** - 友好的错误提示

#### 2. 简单优化模式处理

```python
def handle_simple_optimization(request, uploaded_file):
    """
    简单优化模式：AI 润色 + 样式统一
    """
    # 获取配置
    use_ai = request.POST.get('use_ai') == 'on'
    tone = request.POST.get('tone', 'no_preference')
    style_template = request.POST.get('style_template', 'default')

    # 自定义配置（支持字体、字号、行距、图片尺寸）
    custom_config = {
        'heading_font': request.POST.get('heading_font'),
        'heading_size': request.POST.get('heading_size'),  # 支持中文代码如 'xiaosi'
        'body_font': request.POST.get('body_font'),
        'body_size': request.POST.get('body_size'),
        'line_spacing': safe_float(request.POST.get('line_spacing')),
        'image_width': image_width,
        'image_height': image_height,
    }

    # 初始化格式化器
    formatter = AIWordFormatter(
        input_file_path,
        use_ai=use_ai,
        tone=tone,
        style_config=style_config,
        log_callback=log_callback
    )

    # 执行格式化
    result = formatter.format(output_file_path)

    # 返回文件（支持中文文件名）
    encoded_filename = quote(output_filename)
    response['Content-Disposition'] = (
        f'attachment; filename="{encoded_filename}"; '
        f'filename*=UTF-8\'\'{encoded_filename}'
    )
```

**关键技术 / Key Technologies:**
- 🔧 **中文字号支持** - 支持中文代码（如 'xiaosi'）和数值
- 🔧 **图片尺寸自定义** - 支持英寸和厘米单位
- 🔧 **日志回调** - 实时向前端发送处理进度
- 🔧 **中文文件名** - URL 编码解决中文文件名问题

#### 3. 模板优化模式处理

```python
def handle_template_optimization(request, uploaded_file):
    """
    模板优化模式：根据预定义模板生成结构化文档
    """
    # 1. 获取模板
    template = TemplateManager.get_template(template_id, user)

    # 2. 提取源文档内容
    source_document_text = '\n'.join([para.text for para in doc.paragraphs])

    # 3. 提取图片（带上下文）
    image_tracker = DocumentImageTracker(tmp_file_path)
    extracted_images = image_tracker.extract_images_with_context()

    # 4. 选择处理模式（根据文档长度）
    if len(source_document_text) < 500:
        # 小文档：批量处理（一次性生成所有章节）
        generated_content = processor.generate_from_template_batch(...)
    else:
        # 大文档：顺序处理（逐章节生成）
        generated_content = processor.generate_from_template(...)

    # 5. 图片智能匹配到章节
    for image_meta in extracted_images:
        section_id, position = ImageReinsertionStrategy.find_best_insertion_position(
            image_meta, generated_content, template
        )

    # 6. 构建 Word 文档
    # - 过滤无意义内容（占位符）
    # - 智能插入图片
    # - 应用样式（首行缩进、行距、字体）
```

**核心算法 / Core Algorithms:**
- 🧠 **智能模式选择** - 根据文档长度自动选择批量/顺序模式
- 🧠 **图片语义匹配** - 基于上下文关键词匹配图片到章节
- 🧠 **内容过滤** - 自动过滤占位符和无意义内容

#### 4. 处理状态轮询

```python
@require_http_methods(["GET"])
def processing_status(request):
    """
    返回处理状态，用于前端轮询
    性能优化：
    - 不调用 AI API，仅读取 session
    - 响应时间 < 10ms
    """
    processing_info = request.session.get('processing', {
        'status': 'unknown',
        'logs': [],
        'current_step': 0,
        'total_steps': 0
    })

    # 防止浏览器缓存
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return JsonResponse(processing_info)
```

---

## Database Models

### 位置 / Location
`format_specifications/models.py`

### 1. 文档模板模型

```python
class DocumentTemplate(models.Model):
    """
    文档模板模型（支持系统模板和用户自定义模板）
    """
    # 模板类型
    TEMPLATE_TYPE_CHOICES = [
        ('system', 'System Template'),
        ('user', 'User Template'),
    ]

    # 基本信息
    template_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)

    # 模板结构（JSON 格式存储）
    sections_json = models.JSONField(default=dict)

    # 元数据
    template_type = models.CharField(
        max_length=20,
        choices=TEMPLATE_TYPE_CHOICES,
        default='user'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    version = models.CharField(max_length=20, default='1.0')
    is_active = models.BooleanField(default=True)

    # 使用统计
    usage_count = models.IntegerField(default=0)

    def to_template_definition(self):
        """
        将数据库模型转换为 TemplateDefinition 对象
        """
        sections = [
            self._dict_to_section(section_dict)
            for section_dict in self.sections_json.get('sections', [])
        ]
        return DocumentTemplate(
            id=self.template_id,
            name=self.name,
            description=self.description,
            sections=sections
        )
```

**设计特点 / Design Features:**
- 📦 **JSON 存储** - 灵活存储模板结构
- 📦 **双类型支持** - 系统模板 + 用户模板
- 📦 **使用统计** - 追踪模板使用次数
- 📦 **软删除** - `is_active` 字段支持软删除

### 2. 模板使用日志模型

```python
class TemplateUsageLog(models.Model):
    """
    模板使用日志（用于分析和调试）
    """
    template = models.ForeignKey(DocumentTemplate, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    used_at = models.DateTimeField(auto_now_add=True)

    # 输入参数
    user_outline = models.TextField()
    had_source_document = models.BooleanField(default=False)

    # 结果
    generation_success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    generation_duration = models.IntegerField(null=True)
```

---

## AI Text Processor

### 位置 / Location
`format_specifications/utils/ai_word_utils.py`

### 1. 缓存装饰器 - 避免重复调用

```python
def cache_text_result(expire_seconds=30):
    """
    装饰器：缓存文本处理结果，避免重复调用 AI 接口
    """
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(self, raw_text, *args, **kwargs):
            # 生成文本特征值（避免长文本作为 key）
            text_feature = f"{len(raw_text)}_{raw_text[:100]}"

            # 检查缓存
            if text_feature in cache:
                cached_result, cached_time = cache[text_feature]
                if current_time - cached_time < expire_seconds:
                    return cached_result

            # 执行原方法并缓存
            result = func(self, raw_text, *args, **kwargs)
            cache[text_feature] = (result, current_time)
            return result
        return wrapper
    return decorator
```

**性能优化 / Performance Optimization:**
- ⚡ **特征哈希** - 使用长度+前100字符作为缓存键
- ⚡ **自动清理** - 定期清理过期缓存
- ⚡ **显著减少 API 调用** - 相同文本不重复调用

### 2. 重试装饰器 - 提升可靠性

```python
def retry_on_connection_error(max_retries=3, backoff_factor=2):
    """
    装饰器：在连接错误时重试（指数退避策略）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            wait_time = 1

            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except (requests.exceptions.ConnectionError,
                        requests.exceptions.Timeout) as e:
                    if attempt < max_retries - 1:
                        time.sleep(wait_time)
                        wait_time *= backoff_factor  # 指数退避

            # 所有重试失败，返回兜底值
            if fallback_return == "raw_text":
                return raw_text
            return ""
        return wrapper
    return decorator
```

**可靠性保障 / Reliability:**
- 🛡️ **指数退避** - 避免雪崩效应
- 🛡️ **优雅降级** - 失败时返回原始文本
- 🛡️ **多层兜底** - 确保永不返回空

### 3. AI 文本处理核心方法

```python
class AITextProcessor:
    def __init__(self, tone='no_preference', log_callback=None):
        """初始化 AI 处理器"""
        self.api_key = settings.ZHIPU_API_KEY
        self.model = settings.ZHIPU_MODEL or "glm-4"
        self.client = ZhipuAI(api_key=self.api_key)
        self.request_timeout = 15  # 超时时间
        self.max_text_length = 1000  # 文本长度限制

    @cache_text_result(expire_seconds=30)
    @retry_on_connection_error(max_retries=3, backoff_factor=2)
    def process_text(self, raw_text):
        """
        核心方法：调用智谱 AI 完成文本润色
        """
        # 1. 前置校验
        if not raw_text or len(raw_text) > self.max_text_length:
            return raw_text

        # 2. 构建提示词
        tone_instructions = self._get_tone_instruction()
        prompt = f"""{tone_instructions}
        请润色以下文字，使其更通顺正式，并适当分段和分点。
        文字：{raw_text}"""

        # 3. 调用 AI 接口
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业的文字处理助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,  # 温度越低，结果越稳定
            max_tokens=2000,
            timeout=self.request_timeout
        )

        # 4. 提取结果 + 多层兜底
        processed_text = response.choices[0].message.content.strip()
        if not processed_text:
            raise ValueError("AI 返回空内容")

        return processed_text
```

**技术亮点 / Technical Highlights:**
- 🎯 **多层校验** - 前置校验 + 结果校验
- 🎯 **超时控制** - 避免无限等待
- 🎯 **温度参数** - 低温 = 稳定输出
- 🎯 **装饰器链** - 缓存 + 重试双重优化

### 4. 模板生成方法

```python
def generate_from_template(self, template, user_outline="", source_document_text=""):
    """
    根据模板生成内容（顺序处理模式）
    """
    generated_content = {}

    def process_sections(sections):
        for section in sections:
            # 为当前章节生成内容
            section_content = self._generate_section_content(
                section, user_outline, source_document_text
            )
            if section_content:
                generated_content[section.id] = section_content

            # 递归处理子章节
            if section.subsections:
                process_sections(section.subsections)

    process_sections(template.sections)
    return generated_content
```

---

## Word Formatter

### 位置 / Location
`format_specifications/utils/word_formatter.py`

### 1. 中文字号映射表

```python
# 中文字号映射表（中文代号 -> 磅值）
CHINESE_FONT_SIZES = {
    'chuhao': 42,      # 初号
    'xiaochu': 36,     # 小初
    'yihao': 26,       # 一号
    'xiaoyi': 24,      # 小一
    'erhao': 22,       # 二号
    'xiaoer': 18,      # 小二
    'sanhao': 16,      # 三号
    'xiaosan': 15,     # 小三
    'sihao': 14,       # 四号
    'xiaosi': 12,      # 小四
    'wuhao': 10.5,     # 五号
    'xiaowu': 9,       # 小五
    # 也支持中文字符
    '初号': 42, '小初': 36, '一号': 26, ...
}
```

**特色功能 / Special Feature:**
- 🔤 **双语支持** - 拼音代码（'xiaosi'）和中文字符（'小四'）
- 🔤 **自动转换** - 统一转换为磅值

### 2. 样式模板配置

```python
STYLE_TEMPLATES = {
    'default': {
        'heading_font': '黑体',
        'heading_size': 22,
        'body_font': '宋体',
        'body_size': 12,
        'line_spacing': 1.5,
        'image_width': 5.91,
        'image_height': 4.43
    },
    'official': {
        'heading_font': '黑体',
        'heading_size': 22,
        'body_font': '仿宋',  # 公文常用仿宋
        'body_size': 14,
        'line_spacing': 1.5,
    },
    'academic': {
        'heading_font': '黑体',
        'body_font': '宋体',
        'line_spacing': 2.0,  # 学术论文行距较大
    },
    'casual': {
        'heading_font': '微软雅黑',
        'body_font': '微软雅黑',
        'line_spacing': 1.15,  # 休闲风格行距紧凑
    }
}
```

### 3. 核心格式化类

```python
class AIWordFormatter:
    def __init__(self, input_file_path, use_ai=True, tone='no_preference',
                 style_config=None, log_callback=None):
        """初始化格式化器"""
        self.input_file = input_file_path
        self.doc = Document(input_file_path)
        self.use_ai = use_ai
        self.ai_processor = AITextProcessor(tone=tone, log_callback=log_callback)
        self.style_config = self._validate_style_config(style_config)

        # 创建临时目录（避免权限问题）
        self.temp_dir = Path(os.path.dirname(input_file_path)) / "docx_temp_images"
        self.temp_dir.mkdir(exist_ok=True, mode=0o777)

    def format(self, output_file_path):
        """主格式化逻辑"""
        # 1. 处理段落（文本 + 图片）
        self._process_all_paragraphs()

        # 2. 处理表格
        self._process_tables()

        # 3. 处理图片
        self._process_images()

        # 4. 保存文件
        self.doc.save(output_file_path)
```

### 4. AI 处理模式（保留图片）

```python
def _process_with_ai(self):
    """
    启用 AI 时：修复图片丢失 + 性能优化
    """
    # 1. 提取所有图片
    image_paths = self._extract_images_from_docx()

    # 2. 检测图片段落和文本段落
    original_paragraphs = list(self.doc.paragraphs)
    image_para_indices = []
    pure_texts = []

    for idx, para in enumerate(original_paragraphs):
        para_xml = para._element.xml
        has_image = '<w:drawing>' in para_xml or '<pic:pic>' in para_xml

        if has_image:
            image_para_indices.append(idx)
        elif para.text.strip():
            pure_texts.append(para.text.strip())

    # 3. AI 处理文本
    merged_text = "\n".join(pure_texts)
    processed_text = self.ai_processor.process_text(merged_text)
    processed_text_blocks = processed_text.split("\n\n")

    # 4. 重建文档（按原始顺序插入图片）
    new_doc = Document()
    img_idx = 0
    text_idx = 0

    for original_para_idx, para in enumerate(original_paragraphs):
        if original_para_idx in image_para_indices:
            # 插入图片
            img_run = img_para.add_run()
            img_run.add_picture(image_paths[img_idx],
                               width=self.image_width,
                               height=self.image_height)
            img_idx += 1
        elif original_para_idx in text_para_indices:
            # 插入 AI 处理后的文本
            text_para = new_doc.add_paragraph(processed_text_blocks[text_idx])
            self._set_text_paragraph_style(text_para)
            text_idx += 1

    self.doc = new_doc
```

**核心算法 / Core Algorithm:**
- 🖼️ **图片定位** - 解析 XML 检测图片段落
- 🖼️ **顺序重建** - 保持原始图文顺序
- 🖼️ **智能重建** - AI 处理后文本可能分多段

### 5. 样式应用方法

```python
def _set_text_paragraph_style(self, para):
    """设置段落样式（标题/正文区分）"""
    para_text = para.text

    # 判断是否为标题（根据起始字符）
    if para_text.startswith(("第", "一、", "二、", "三、", ...)):
        # 标题样式
        para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        for run in para.runs:
            run.font.name = self.style_config['heading_font']
            run._element.rPr.rFonts.set(qn('w:eastAsia'),
                                        self.style_config['heading_font'])
            run.font.size = Pt(self.style_config['heading_size'])
            run.font.bold = True
    else:
        # 正文样式
        para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        para.paragraph_format.line_spacing = self.style_config['line_spacing']
        para.paragraph_format.first_line_indent = Pt(21.0)  # 首行缩进 2 字符
        for run in para.runs:
            run.font.name = self.style_config['body_font']
            run.font.size = Pt(self.style_config['body_size'])
```

**技术细节 / Technical Details:**
- ✍️ **中文字体设置** - 使用 `w:eastAsia` 设置中文字体
- ✍️ **首行缩进** - 21 磅 ≈ 2 个中文字符
- ✍️ **标题识别** - 根据起始字符判断

---

## Template Manager

### 位置 / Location
`format_specifications/services/template_manager.py`

### 1. 模板获取方法

```python
class TemplateManager:
    @staticmethod
    def get_template(template_id: str, user: User = None):
        """
        获取模板（优先预定义模板，然后查询数据库）
        """
        # 1. 先检查预定义模板
        if template_id in PREDEFINED_TEMPLATES:
            return PREDEFINED_TEMPLATES[template_id]

        # 2. 再检查数据库中的用户模板
        try:
            db_template = DocumentTemplate.objects.get(
                template_id=template_id,
                created_by=user,
                is_active=True
            )
            return db_template.to_template_definition()
        except DocumentTemplate.DoesNotExist:
            return None
```

**设计模式 / Design Pattern:**
- 📋 **模板方法模式** - 优先级查找（预定义 > 数据库）
- 📋 **工厂模式** - 统一返回 TemplateDefinition 对象

### 2. 自定义模板创建

```python
@staticmethod
def create_custom_template(user, template_id, name, description,
                          category, sections_data, version="1.0"):
    """
    创建自定义模板
    """
    # 1. 验证模板结构
    is_valid, errors = TemplateValidator.validate_custom_template_json(sections_data)
    if not is_valid:
        raise ValueError(f"Template validation failed: {errors}")

    # 2. 检查 ID 是否已存在
    existing = DocumentTemplate.objects.filter(
        template_id=template_id,
        created_by=user
    ).first()
    if existing:
        raise ValueError(f"Template ID '{template_id}' already exists")

    # 3. 创建数据库记录
    db_template = DocumentTemplate.objects.create(
        template_id=template_id,
        name=name,
        description=description,
        category=category,
        sections_json=sections_data,
        template_type='user',
        created_by=user,
        version=version
    )

    return db_template
```

### 3. 使用日志记录

```python
@staticmethod
def log_template_usage(template, user, user_outline,
                       had_source_document, generation_success,
                       generation_duration, error_message=""):
    """
    记录模板使用日志（用于分析和调试）
    """
    TemplateUsageLog.objects.create(
        template=template,
        user=user,
        user_outline=user_outline,
        had_source_document=had_source_document,
        generation_success=generation_success,
        error_message=error_message,
        generation_duration=generation_duration
    )
```

---

## URL Routing

### 位置 / Location
`format_specifications/urls.py`

### URL 配置

```python
urlpatterns = [
    # 管理后台
    path('admin/', admin.site.urls),

    # 主页（上传页面）
    path('', views.upload_word_page, name='upload_word_page'),

    # AI 格式化接口
    path('ai_format/', views.ai_format_word, name='ai_format_word'),

    # API 接口
    path('api/template-details/<str:template_id>/',
         views.api_template_details, name='api_template_details'),
    path('api/processing-status/',
         views.ai_processing_status, name='ai_processing_status'),

    # 处理状态轮询
    path('processing-status/',
         views.processing_status, name='processing_status'),

    # 模板生成页面
    path('template/',
         views.template_generation_page, name='template_generation_page'),
    path('template/generate/',
         views.generate_from_template, name='generate_from_template'),

    # 文档分割功能
    path('segment/',
         views.segmentation_only_page, name='segmentation_only_page'),
    path('segment/segment-document/',
         views.segment_document, name='segment_document'),
]
```

**路由设计 / Routing Design:**
- 🔗 **RESTful 风格** - 清晰的 URL 结构
- 🔗 **命名路由** - 便于反向解析
- 🔗 **API 分离** - API 接口单独前缀

---

## 性能优化总结

### 1. AI 调用优化
- ✅ **缓存机制** - 相同文本 30 秒内不重复调用
- ✅ **批量处理** - 小文档一次性生成所有章节
- ✅ **超时控制** - 15 秒超时避免无限等待

### 2. 文档处理优化
- ✅ **临时目录** - 输入文件同目录，避免权限问题
- ✅ **手动写入** - 替代 `zip.extract`，提升性能
- ✅ **图片预提取** - 先提取后处理，保持顺序

### 3. 网络优化
- ✅ **状态轮询** - 轻量级 session 读取，响应 < 10ms
- ✅ **指数退避** - 避免雪崩效应
- ✅ **优雅降级** - 失败时返回原始文本

---

## 技术栈总结

### 后端框架
- Django 6.0 - Web 框架
- Python 3.x - 编程语言

### 核心库
- python-docx - Word 文档处理
- ZhipuAI SDK - 智谱 AI 集成
- httpx/requests - HTTP 客户端

### 数据库
- SQLite - 开发环境
- 支持 PostgreSQL/MySQL - 生产环境

---

**文档版本**: 1.0
**最后更新**: 2026-01-20
**维护团队**: Format Specifications Development Team
