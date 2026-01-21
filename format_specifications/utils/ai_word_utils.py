from zhipuai import ZhipuAI
from django.conf import settings
import logging
import time
from functools import wraps
import requests
from zhipuai.core import _errors
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Callable

# 配置独立日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def cache_text_result(expire_seconds=30):
    """
    装饰器：缓存文本处理结果，避免重复调用 AI 接口（提升性能，减少超时概率）
    :param expire_seconds: 缓存有效期（秒），默认 30 秒
    """
    cache = {}  # key: 文本特征值，value: (处理结果, 缓存时间戳)

    def decorator(func):
        @wraps(func)
        def wrapper(self, raw_text, *args, **kwargs):
            # 生成文本特征值（避免长文本作为 key，节省内存）
            raw_text_strip = raw_text.strip() if raw_text else ""
            text_feature = f"{len(raw_text_strip)}_{raw_text_strip[:100]}"  # 长度+前100字符

            # 检查缓存：未过期则直接返回缓存结果
            current_time = time.time()
            if text_feature in cache:
                cached_result, cached_time = cache[text_feature]
                if current_time - cached_time < expire_seconds:
                    logger.info(f"命中文本缓存，直接返回结果（无需重复调用 AI）")
                    return cached_result

            # 未命中缓存：执行原方法
            result = func(self, raw_text, *args, **kwargs)

            # 缓存结果
            cache[text_feature] = (result, current_time)

            # 清理过期缓存（避免内存泄露）
            for feature in list(cache.keys()):
                if current_time - cache[feature][1] > expire_seconds:
                    del cache[feature]

            return result
        return wrapper
    return decorator


def retry_on_connection_error(max_retries=3, backoff_factor=2, fallback_return=""):
    """
    装饰器：在连接错误时重试 AI 调用（指数退避策略）

    :param max_retries: 最大重试次数（默认 3 次）
    :param backoff_factor: 退避因子（默认 2，即每次重试等待时间翻倍）
    :param fallback_return: 失败时的返回值（默认空字符串，可设置为 'raw_text' 返回原始文本）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            wait_time = 1  # 初始等待时间（秒）

            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"AI 接口连接失败（第 {attempt + 1} 次尝试），{wait_time} 秒后重试...")
                        self.log_callback(f"⚠️ 连接失败，{wait_time} 秒后重试 ({attempt + 1}/{max_retries})...")
                        time.sleep(wait_time)
                        wait_time *= backoff_factor  # 指数退避
                    else:
                        logger.error(f"AI 接口连接失败，已达最大重试次数 ({max_retries})")
                        self.log_callback(f"❌ 连接失败，已达最大重试次数")

                except Exception as e:
                    # 其他异常直接抛出，不重试
                    raise e

            # 所有重试都失败后，返回 fallback 值
            if fallback_return == "raw_text" and args:
                # 对于 process_text 方法，返回原始文本
                raw_text = args[0] if args else ""
                raw_text_strip = raw_text.strip() if raw_text else ""
                logger.error(f"AI 处理失败（连接错误），返回原始文本: {str(last_exception)}")
                self.log_callback(f"⚠️ AI 连接失败，返回原始文本")
                return raw_text_strip
            else:
                # 对于其他方法，返回空字符串
                logger.error(f"AI 处理失败（连接错误），返回空值: {str(last_exception)}")
                self.log_callback(f"⚠️ AI 连接失败，跳过此部分")
                return ""

        return wrapper
    return decorator

class AITextProcessor:
    def __init__(self, tone='no_preference', log_callback=None):
        """
        初始化智谱 AI 客户端，配置超时参数

        参数:
        - tone: 文档语调 (no_preference, direct, rigorous, empathetic, inspirational, humorous, cold_sharp)
        - log_callback: 日志回调函数 (可选)
        """
        # 从 Django 配置中读取 API 密钥和模型（避免硬编码）
        self.api_key = settings.ZHIPU_API_KEY
        self.model = settings.ZHIPU_MODEL or "glm-4"
        self.client = ZhipuAI(api_key=self.api_key)

        # 语调设置
        self.tone = tone

        # 日志回调函数
        self.log_callback = log_callback or (lambda msg: logger.info(msg))

        # 性能优化：设置接口超时时间（避免无限等待，默认 15 秒）
        self.request_timeout = 15
        # 性能优化：限制单次处理文本最大长度（避免超大文本超时，可根据模型调整）
        self.max_text_length = 1000

        logger.info("AI 文本处理器初始化完成（超时时间：%d 秒，最大文本长度：%d 字符，语调：%s）",
                    self.request_timeout, self.max_text_length, tone)

    @cache_text_result(expire_seconds=30)
    @retry_on_connection_error(max_retries=3, backoff_factor=2, fallback_return="raw_text")
    def process_text(self, raw_text):
        """
        核心方法：调用智谱 AI 完成文本润色，解决返回空 + 避免超时

        :param raw_text: 原始大段文字
        :return: AI 处理后的结构化文字（永不返回空，异常时返回原始文本）
        """
        # 第一步：前置校验（避免无意义调用，提升性能）
        if not raw_text or not raw_text.strip():
            logger.error("原始文本为空，无需处理")
            return ""  # 兜底返回空字符串，不返回 None

        raw_text_strip = raw_text.strip()

        # 第二步：超长文本限制（避免 AI 处理耗时过久导致超时）
        if len(raw_text_strip) > self.max_text_length:
            logger.warning(f"文本过长（{len(raw_text_strip)} 字符），超过单次处理上限（{self.max_text_length} 字符），返回原始文本避免超时")
            return raw_text_strip

        # 第三步：构建语调提示词
        tone_instructions = self._get_tone_instruction()

        # 第四步：构建简洁 Prompt（减少 AI 思考时间，提升响应速度）
        prompt = f"""{tone_instructions}
请润色以下文字，使其更通顺正式，并适当分段和分点，直接返回处理后的文字，不要额外解释。
文字：{raw_text_strip}"""

        try:
            # 第五步：调用智谱 AI 接口（设置超时，避免无限等待）
            self.log_callback("正在调用 AI 处理文本...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的文字处理助手，擅长结构化文本优化。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 温度越低，结果越稳定，处理速度越快
                max_tokens=2000,
                timeout=self.request_timeout  # 核心：设置接口超时时间
            )

            # 第六步：提取结果 + 多层兜底校验（避免返回空）
            raw_content = getattr(response.choices[0].message, "content", "") or ""
            processed_text = raw_content.strip()

            # 校验处理结果：为空则抛出异常，进入兜底逻辑
            if not processed_text:
                logger.error("AI 返回空内容（接口响应正常，但内容为空）")
                raise ValueError("AI 返回空内容，处理失败")

            logger.info(f"AI 文本处理完成，返回文本长度: {len(processed_text)} 字符")
            self.log_callback(f"✅ 文本处理完成 ({len(processed_text)} 字符)")
            return processed_text

        # 针对性捕获：超时异常（最易导致空内容的性能问题）
        except requests.exceptions.Timeout:
            error_msg = f"AI 接口请求超时（超过 {self.request_timeout} 秒），返回原始文本"
            logger.error(error_msg)
            self.log_callback(f"⚠️ {error_msg}")
            return raw_text_strip

        # 针对性捕获：网络连接异常
        except requests.exceptions.ConnectionError:
            error_msg = "网络连接失败，无法调用 AI 接口，返回原始文本"
            logger.error(error_msg)
            self.log_callback(f"⚠️ {error_msg}")
            return raw_text_strip

        # 针对性捕获：业务逻辑异常（如返回格式错误、空值）
        except (ValueError, AttributeError) as e:
            error_msg = f"AI 文本处理业务异常: {str(e)}，返回原始文本"
            logger.error(error_msg)
            self.log_callback(f"⚠️ {error_msg}")
            return raw_text_strip

    def _get_tone_instruction(self):
        """
        根据语调设置返回相应的提示词

        :return: 语调提示文字符串
        """
        tone_map = {
            'no_preference': "请保持客观、中立的语调。",
            'direct': "请使用简洁、直接的语调，避免冗余表达，直奔主题。",
            'rigorous': "请使用严谨、专业的语调，使用准确的术语和完整的表达。",
            'empathetic': "请使用亲切、温暖的语调，体现关怀和理解。",
            'inspirational': "请使用鼓舞人心的语调，传递积极向上的能量。",
            'humorous': "请使用轻松有趣的语调，可以适当加入幽默元素。",
            'cold_sharp': "请使用权威、果断的语调，直接陈述，不带情感色彩。"
        }

        return tone_map.get(self.tone, "请保持客观、中立的语调。")

    def generate_from_template(
        self,
        template,
        user_outline="",
        source_document_text="",
        tone=None
    ):
        """
        根据模板生成内容（顺序处理模式）

        参数:
        - template: 模板对象
        - user_outline: 用户大纲
        - source_document_text: 源文档文本
        - tone: 语调

        返回:
        - dict: {section_id: generated_content}
        """
        generated_content = {}

        # 递归处理所有章节
        def process_sections(sections):
            for section in sections:
                # 为当前章节生成内容
                section_content = self._generate_section_content(
                    section,
                    user_outline,
                    source_document_text
                )
                if section_content:
                    generated_content[section.id] = section_content
                    self.log_callback(f"✓ 已生成: {section.title}")

                # 递归处理子章节
                if section.subsections:
                    process_sections(section.subsections)

        process_sections(template.sections)
        return generated_content

    def generate_from_template_batch(
        self,
        template,
        user_outline="",
        source_document_text="",
        tone=None
    ):
        """
        根据模板生成内容（批量处理模式）

        参数:
        - template: 模板对象
        - user_outline: 用户大纲
        - source_document_text: 源文档文本
        - tone: 语调

        返回:
        - dict: {section_id: generated_content}
        """
        # 批量模式：一次性处理所有章节
        generated_content = {}

        # 构建所有章节的提示
        sections_info = []
        def collect_sections(sections):
            for section in sections:
                sections_info.append(f"- {section.title}")
                if section.subsections:
                    collect_sections(section.subsections)

        collect_sections(template.sections)

        # 构建批量提示词
        tone_instruction = self._get_tone_instruction()
        sections_list = "\n".join(sections_info)

        prompt = f"""{tone_instruction}

请根据以下模板结构，为每个章节生成内容。

模板章节：
{sections_list}

用户大纲：{user_outline}

源文档内容：{source_document_text[:2000]}

请为每个章节生成详细内容，按照以下格式返回：
章节1标题
[章节1内容]

章节2标题
[章节2内容]

...

请确保内容专业、完整，每个章节至少200字。"""

        try:
            self.log_callback("正在批量生成所有章节内容...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是专业的内容生成助手，擅长根据模板结构生成高质量的文档内容。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=4000,
                timeout=self.request_timeout
            )

            content = response.choices[0].message.content.strip()

            # 解析返回的内容，分配到各个章节
            current_section = None
            current_content = []

            def assign_sections(sections):
                for section in sections:
                    if current_section and current_content:
                        generated_content[current_section.id] = "\n".join(current_content)
                        self.log_callback(f"✓ 已生成: {section.title}")
                        current_content.clear()

                    current_section = section

                    if section.subsections:
                        assign_sections(section.subsections)

                # 最后一个章节
                if current_section and current_content:
                    generated_content[current_section.id] = "\n".join(current_content)

            assign_sections(template.sections)

            return generated_content

        except Exception as e:
            logger.error(f"批量生成失败: {str(e)}")
            self.log_callback(f"⚠️ 批量生成失败: {str(e)}")
            # 降级到顺序处理模式
            self.log_callback("降级到顺序处理模式...")
            return self.generate_from_template(template, user_outline, source_document_text, tone)

    def generate_from_template_parallel(
        self,
        template,
        user_outline="",
        source_document_text="",
        tone=None,
        max_workers=5
    ):
        """
        根据模板生成内容（并行处理模式）

        使用多线程并发处理多个章节，显著提升处理速度

        参数:
        - template: 模板对象
        - user_outline: 用户大纲
        - source_document_text: 源文档文本
        - tone: 语调
        - max_workers: 最大并发线程数（默认5，根据API限流可调整）

        返回:
        - dict: {section_id: generated_content}
        """
        generated_content = {}

        # 收集所有需要处理的章节（包括子章节）
        all_sections = []

        def collect_sections(sections, level=1):
            for section in sections:
                all_sections.append(section)
                if section.subsections:
                    collect_sections(section.subsections, level + 1)

        collect_sections(template.sections)

        self.log_callback(f"🚀 并行处理模式：同时处理 {len(all_sections)} 个章节（{max_workers} 线程并发）")

        # 定义处理单个章节的函数
        def process_single_section(section):
            """处理单个章节并返回结果"""
            try:
                section_content = self._generate_section_content(
                    section,
                    user_outline,
                    source_document_text
                )
                if section_content:
                    return (section.id, section_content, section.title, None)
                else:
                    return (section.id, "", section.title, "生成内容为空")
            except Exception as e:
                logger.error(f"处理章节 '{section.title}' 时出错: {str(e)}")
                return (section.id, "", section.title, str(e))

        # 使用线程池并行处理所有章节
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_section = {
                executor.submit(process_single_section, section): section
                for section in all_sections
            }

            # 收集完成的任务
            completed = 0
            total = len(all_sections)

            for future in as_completed(future_to_section):
                section = future_to_section[future]
                try:
                    section_id, content, title, error = future.result()

                    if error:
                        self.log_callback(f"⚠️ 失败: {title} - {error}")
                    elif content:
                        generated_content[section_id] = content
                        completed += 1
                        self.log_callback(f"✓ 已生成 [{completed}/{total}]: {title}")

                except Exception as e:
                    logger.error(f"处理章节时发生异常: {str(e)}")
                    self.log_callback(f"⚠️ 异常: {section.title}")

        self.log_callback(f"✅ 并行处理完成：成功生成 {len(generated_content)}/{total} 个章节")
        return generated_content

    @retry_on_connection_error(max_retries=3, backoff_factor=2)
    def extract_section_for_structure(self, source_text, section_title):
        """
        为自定义结构提取相关内容

        参数:
        - source_text: 源文本
        - section_title: 章节标题

        返回:
        - str: 提取的相关内容
        """
        # 使用AI提取与章节相关的内容
        prompt = f"""请从以下文本中提取与"{section_title}"相关的所有内容。

源文本：
{source_text[:3000]}

请只返回相关的内容片段，不要添加任何解释或总结。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业的内容提取助手，擅长从文档中提取特定主题的相关内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=2000,
            timeout=self.request_timeout
        )

        extracted = response.choices[0].message.content.strip()
        logger.info(f"为章节 '{section_title}' 提取了 {len(extracted)} 字符")
        return extracted

    def extract_sections_for_structure_parallel(
        self,
        source_text: str,
        section_titles: List[str],
        max_workers: int = 5
    ) -> Dict[str, str]:
        """
        并行提取多个章节的相关内容

        参数:
        - source_text: 源文本
        - section_titles: 章节标题列表
        - max_workers: 最大并发线程数

        返回:
        - dict: {section_title: extracted_content}
        """
        self.log_callback(f"🚀 并行提取：同时处理 {len(section_titles)} 个章节")

        def extract_single_section(section_title: str) -> tuple:
            """提取单个章节的内容"""
            try:
                content = self.extract_section_for_structure(source_text, section_title)
                return (section_title, content, None)
            except Exception as e:
                logger.error(f"提取章节 '{section_title}' 时出错: {str(e)}")
                return (section_title, "", str(e))

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(extract_single_section, title): title
                for title in section_titles
            }

            completed = 0
            for future in as_completed(futures):
                section_title, content, error = future.result()
                if error:
                    self.log_callback(f"⚠️ 提取失败: {section_title}")
                else:
                    results[section_title] = content
                    completed += 1
                    self.log_callback(f"✓ 已提取 [{completed}/{len(section_titles)}]: {section_title}")

        self.log_callback(f"✅ 并行提取完成：成功提取 {len(results)}/{len(section_titles)} 个章节")
        return results

    def polish_sections_parallel(
        self,
        sections_data: Dict[str, str],
        max_workers: int = 5
    ) -> Dict[str, str]:
        """
        并行润色多个章节的内容

        参数:
        - sections_data: {section_title: raw_content} 字典
        - max_workers: 最大并发线程数

        返回:
        - dict: {section_title: polished_content}
        """
        self.log_callback(f"🚀 并行润色：同时处理 {len(sections_data)} 个章节")

        def polish_single_section(item: tuple) -> tuple:
            """润色单个章节"""
            section_title, raw_content = item
            try:
                if not raw_content or len(raw_content.strip()) < 10:
                    return (section_title, "", "内容过短")
                polished = self.process_text(raw_content)
                return (section_title, polished, None)
            except Exception as e:
                logger.error(f"润色章节 '{section_title}' 时出错: {str(e)}")
                return (section_title, "", str(e))

        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(polish_single_section, item): item[0]
                for item in sections_data.items()
            }

            completed = 0
            for future in as_completed(futures):
                section_title, polished, error = future.result()
                if error:
                    results[section_title] = ""
                    self.log_callback(f"⚠️ 润色失败: {section_title}")
                else:
                    results[section_title] = polished
                    completed += 1
                    self.log_callback(f"✓ 已润色 [{completed}/{len(sections_data)}]: {section_title}")

        self.log_callback(f"✅ 并行润色完成：成功润色 {len([r for r in results.values() if r])}/{len(sections_data)} 个章节")
        return results

    def segment_text(self, text, mode="paragraph", include_metadata=False):
        """
        分割文本

        参数:
        - text: 要分割的文本
        - mode: 分割模式 (paragraph/sentence/semantic)
        - include_metadata: 是否包含元数据

        返回:
        - list: 分割后的文本片段列表（或字典列表，如果 include_metadata=True）
        """
        if mode == "paragraph":
            segments = text.split("\n\n")
        elif mode == "sentence":
            import re
            segments = re.split(r'[。！？\.!?]', text)
            segments = [s.strip() for s in segments if s.strip()]
        elif mode == "semantic":
            # 语义分割：按段落分割（简单实现）
            segments = text.split("\n\n")
        else:
            segments = [text]

        if include_metadata:
            return [
                {
                    "type": mode,
                    "text": segment,
                    "position": i
                }
                for i, segment in enumerate(segments)
            ]
        else:
            return segments

    @retry_on_connection_error(max_retries=3, backoff_factor=2)
    def _generate_section_content(self, section, user_outline, source_text):
        """
        为单个章节生成内容

        参数:
        - section: 章节对象
        - user_outline: 用户大纲
        - source_text: 源文本

        返回:
        - str: 生成的内容
        """
        tone_instruction = self._get_tone_instruction()

        prompt = f"""{tone_instruction}

请为以下章节生成详细内容：

章节标题：{section.title}

章节描述：{section.title}

用户提供的要点：{user_outline}

源文档参考内容：{source_text[:1500] if source_text else "无"}

请生成该章节的详细内容（至少300字），要求：
1. 内容专业、完整
2. 条理清晰、逻辑严密
3. 符合章节主题
4. 可以适当使用分点说明

直接返回生成的内容，不要包含章节标题。"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是专业的内容生成助手，擅长根据模板和源文档生成高质量的章节内容。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000,
            timeout=self.request_timeout
        )

        content = response.choices[0].message.content.strip()

        # 检查是否太短
        if len(content) < 50:
            logger.warning(f"章节 '{section.title}' 生成的内容过短 ({len(content)} 字符)")
            return ""

        return content