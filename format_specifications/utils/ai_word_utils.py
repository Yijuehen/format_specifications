from zhipuai import ZhipuAI
from django.conf import settings
import logging
import time
from functools import wraps
import requests

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

class AITextProcessor:
    def __init__(self):
        """初始化智谱 AI 客户端，配置超时参数"""
        # 从 Django 配置中读取 API 密钥和模型（避免硬编码）
        self.api_key = settings.ZHIPU_API_KEY
        self.model = settings.ZHIPU_MODEL or "glm-4"
        self.client = ZhipuAI(api_key=self.api_key)
        
        # 性能优化：设置接口超时时间（避免无限等待，默认 15 秒）
        self.request_timeout = 15
        # 性能优化：限制单次处理文本最大长度（避免超大文本超时，可根据模型调整）
        self.max_text_length = 1000
        
        logger.info("AI 文本处理器初始化完成（超时时间：%d 秒，最大文本长度：%d 字符）",
                    self.request_timeout, self.max_text_length)

    @cache_text_result(expire_seconds=30)
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
        
        # 第三步：构建简洁 Prompt（减少 AI 思考时间，提升响应速度）
        prompt = f"""请润色以下文字，使其更通顺正式，并适当分段和分点，直接返回处理后的文字，不要额外解释。
文字：{raw_text_strip}"""

        try:
            # 第四步：调用智谱 AI 接口（设置超时，避免无限等待）
            logger.info("正在调用智谱 AI 接口...")
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

            # 第五步：提取结果 + 多层兜底校验（避免返回空）
            raw_content = getattr(response.choices[0].message, "content", "") or ""
            processed_text = raw_content.strip()

            # 校验处理结果：为空则抛出异常，进入兜底逻辑
            if not processed_text:
                logger.error("AI 返回空内容（接口响应正常，但内容为空）")
                raise ValueError("AI 返回空内容，处理失败")

            logger.info(f"AI 文本处理完成，返回文本长度: {len(processed_text)} 字符")
            return processed_text
        
        # 针对性捕获：超时异常（最易导致空内容的性能问题）
        except requests.exceptions.Timeout:
            logger.error(f"AI 接口请求超时（超过 {self.request_timeout} 秒），返回原始文本")
            return raw_text_strip
        
        # 针对性捕获：网络连接异常
        except requests.exceptions.ConnectionError:
            logger.error("网络连接失败，无法调用 AI 接口，返回原始文本")
            return raw_text_strip
        
        # 针对性捕获：业务逻辑异常（如返回格式错误、空值）
        except (ValueError, AttributeError) as e:
            logger.error(f"AI 文本处理业务异常: {str(e)}，返回原始文本")
            return raw_text_strip
        
        # 最终兜底：捕获所有未知异常，确保永不返回空
        except Exception as e:
            logger.error(f"AI 文本处理未知失败: {str(e)}，返回原始文本")
            return raw_text_strip