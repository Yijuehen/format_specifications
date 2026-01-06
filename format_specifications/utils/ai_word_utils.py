from zhipuai import ZhipuAI  # 导入智谱官方 SDK
from django.conf import settings
import logging

# 获取logger实例
logger = logging.getLogger(__name__)

class AITextProcessor:
    def __init__(self):
        # 初始化智谱 AI 客户端（官方标准方式）
        self.client = ZhipuAI(
            api_key=settings.ZHIPU_API_KEY,
        )
        logger.info("AI文本处理器初始化完成")

    def process_text(self, raw_text):
        """
        核心方法：调用智谱 AI 完成润色、分段、分点
        :param raw_text: 原始大段文字
        :return: AI 处理后的结构化文字（含分段、分点标记）
        """
        logger.info(f"开始AI文本处理，原始文本长度: {len(raw_text)} 字符")
        
        prompt = f"""
        请你作为专业的文字编辑，对以下文字进行3项处理：
        1. 润色：修正语法错误，优化语句通顺度，使用正式书面语，保留原文核心含义。
        2. 分段：根据逻辑层次拆分段落（如不同主题、不同论点分开），避免大段文字堆砌。
        3. 分点：识别文字中适合列表化的内容（如步骤、要点、分类等），自动转为有序列表（用1.、2.标记）或无序列表（用-标记），列表项需简洁明了。
        
        处理要求：
        -段首缩进2字符。
        - 保持原文意思不变，不要添加个人观点。
        - 只返回处理后的文字，不要添加任何额外说明。
        - 分段用空行分隔，分点直接用对应的标记（1.、-）开头。
        
        原始文字：{raw_text}
        """

        try:
            # 调用智谱 AI 接口（官方标准 chat.completions 接口）
            logger.info("正在调用智谱AI接口...")
            response = self.client.chat.completions.create(
                model=settings.ZHIPU_MODEL,
                messages=[
                    {"role": "system", "content": "你是专业的文字处理助手，擅长结构化文本优化。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 温度越低，结果越稳定、严谨
                max_tokens=2000  # 根据需要调整，确保能容纳处理后的文字
            )

            # 提取智谱 AI 处理后的文字
            raw_content = getattr(response.choices[0].message, "content", "") or ""
            processed_text = raw_content.strip()
            if not processed_text:
                logger.error("AI返回空内容")
                raise ValueError("AI返回空内容，处理失败")  # 修改错误信息
            logger.info(f"AI文本处理完成，返回文本长度: {len(processed_text)} 字符")
            return processed_text
        except Exception as e:
            logger.error(f"AI文本处理失败: {str(e)}")
            raise e