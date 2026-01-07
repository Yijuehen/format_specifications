from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from docx.oxml.shared import OxmlElement
import os
import logging
import re  # 新增：正则依赖
from .ai_word_utils import AITextProcessor  # 导入 AI 文本处理器

# 获取logger实例
logger = logging.getLogger(__name__)

class AIWordFormatter:
    def __init__(self, input_file_path, use_ai=True):
        self.input_file = input_file_path
        self.doc = Document(input_file_path)
        self.use_ai = use_ai  # 是否启用 AI 处理（可配置开关）
        self.ai_processor = AITextProcessor() if use_ai else None
        self.image_width = Inches(5.91)  # 统一图片宽度：5.91英寸 ≈ 15cm（A4纸宽度的2/3）
        self.image_height = Inches(4.43)  # 统一图片高度：4.43英寸 ≈ 11.25cm（保持16:9比例）
        logger.info(f"AIWordFormatter初始化完成，文件: {input_file_path}, AI启用: {use_ai}")

    def format(self, output_file_path):
        """整合所有格式化逻辑：AI文本处理 + 样式统一 + 图片规范"""
        logger.info(f"开始格式化文件，输入: {self.input_file}，输出: {output_file_path}")
        
        # 1. 处理文本内容（AI 润色、分段、分点 + 样式统一）
        self._process_all_paragraphs()
        logger.info("段落处理完成")
        
        # 2. 处理表格样式
        self._process_tables()
        logger.info("表格处理完成")
        
        # 3. 处理图片大小和对齐
        self._process_images()
        logger.info("图片处理完成")
        
        # 4. 保存格式化后的文件
        self.doc.save(output_file_path)
        logger.info(f"格式化完成，文件已保存: {output_file_path}")
        return output_file_path

    def _process_all_paragraphs(self):
        """处理所有段落：文本整体AI格式化 + 图片原位还原"""
        logger.info("开始处理所有段落（文本+图片）")
        original_paragraphs = list(self.doc.paragraphs)
        total_paragraphs = len(original_paragraphs)
        logger.info(f"检测到 {total_paragraphs} 个原始段落")

        # ===== 核心修改：记录原始文档结构（文本/图片/空段落的位置）=====
        doc_structure = []  # 结构：[(类型, 内容/对象, 索引), ...] 类型：text/image/empty
        pure_texts = []     # 仅存纯文本，用于AI整体处理
        image_mapping = {}  # 图片段落映射：{原始索引: 图片段落对象}

        for idx, para in enumerate(original_paragraphs):
            # 文本检测（兼容全空白字符）
            para_text = para.text.strip()
            has_text = bool(para_text)
            
            # 图片检测（复用你原有的完善逻辑）
            para_xml = para._element.xml
            has_image = (
                '<w:drawing>' in para_xml or  # 新版Office/WPS核心标签
                '<pic:pic>' in para_xml or 
                'a:pic' in para_xml or
                '<v:shape' in para_xml or    # 旧版Word标签
                para._element.xpath('.//w:drawing')  # 补充XPath检测
            )

            logger.info(f"段落 {idx}: 有文本={has_text}, 有图片={has_image}, 文本内容: '{para.text[:50]}...'")

            if has_image:
                # 图片段落：记录位置和对象
                doc_structure.append(("image", para, idx))
                image_mapping[idx] = para
            elif has_text:
                # 文本段落：记录位置和文本
                doc_structure.append(("text", para_text, idx))
                pure_texts.append(para_text)
            else:
                # 空段落：保留结构
                doc_structure.append(("empty", "", idx))
                logger.info(f"段落 {idx} 为空，标记为保留结构的空段落")

        logger.info(f"原始文本段落数: {len(pure_texts)}, 图片段落数: {len(image_mapping)}, 空段落数: {len([x for x in doc_structure if x[0] == 'empty'])}")

        # ===== AI处理纯文本（整体处理，保证逻辑完整）=====
        processed_text_blocks = []
        if pure_texts:
            merged_text = "\n".join(pure_texts)
            if self.use_ai:
                logger.info(f"开始AI处理整体文本（长度：{len(merged_text)}字符）")
                try:
                    processed_text = self.ai_processor.process_text(merged_text)
                    logger.info("AI文本处理完成")
                    # 校验AI返回结果
                    if not processed_text or not processed_text.strip():
                        logger.error("AI返回空内容，终止处理并报错")
                        raise ValueError("AI返回空内容，无法生成格式化文件，请重新上传或稍后重试")
                    # 拆分为AI处理后的文本块（空行分隔）
                    processed_text_blocks = [p.strip() for p in processed_text.split("\n\n") if p.strip()]
                    logger.info(f"AI处理后生成 {len(processed_text_blocks)} 个文本段落")
                except Exception as e:
                    logger.error(f"AI处理出错: {str(e)}，终止处理并报错")
                    raise
            else:
                # 不启用AI：直接使用原始文本块
                logger.info("跳过AI处理，使用原始文本")
                processed_text_blocks = pure_texts
        else:
            logger.warning("无纯文本段落，仅保留图片/空段落")

        # ===== 清空原文档，准备重建 =====
        for para in self.doc.paragraphs:
            para.clear()

        # ===== 按原始结构重建文档（核心：文本+图片原位还原）=====
        text_block_idx = 0  # 指向当前待插入的AI文本块
        for item in doc_structure:
            para_type, content, idx = item

            if para_type == "image":
                # 插入原始图片段落（保留你原有的样式）
                new_img_para = self.doc.add_paragraph()
                for child in content._element:
                    new_img_para._element.append(child)
                new_img_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                new_img_para.paragraph_format.space_after = Pt(12)
                new_img_para.paragraph_format.space_before = Pt(12)
                logger.info(f"重建段落 {idx}：图片段落")

            elif para_type == "text" and text_block_idx < len(processed_text_blocks):
                # 插入AI处理后的文本段落（按原始位置）
                new_text_para = self.doc.add_paragraph()
                text_content = processed_text_blocks[text_block_idx]
                # 复用你原有的文本格式化逻辑（列表/标题/正文）
                if text_content.startswith(("1.", "2.", "3.")):
                    self._add_ordered_list(new_text_para, text_content)
                elif text_content.startswith(("-", "·")):
                    self._add_unordered_list(new_text_para, text_content)
                else:
                    new_text_para.text = text_content
                    if text_content.startswith(("第", "一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、")):
                        self._format_title(new_text_para)
                    else:
                        self._format_body(new_text_para)
                text_block_idx += 1
                logger.info(f"重建段落 {idx}：AI格式化文本段落")

            elif para_type == "empty":
                # 保留空段落（维持原始排版）
                self.doc.add_paragraph("")
                logger.info(f"重建段落 {idx}：空段落")

        # 处理剩余的AI文本块（若有）
        while text_block_idx < len(processed_text_blocks):
            new_para = self.doc.add_paragraph()
            remaining_text = processed_text_blocks[text_block_idx]
            new_para.text = remaining_text
            self._format_body(new_para)
            text_block_idx += 1
            logger.info(f"追加剩余文本段落 {text_block_idx}：{remaining_text[:50]}...")

    def _add_ordered_list(self, para, content):
        """添加有序列表（适配 AI 返回的 1.、2. 格式）"""
        logger.debug(f"处理有序列表: {content[:50]}...")
        # 拆分列表项（按 数字. 拆分，优化正则匹配）
        items = []
        splits = re.split(r'(\d+\.)', content)
        for i in range(1, len(splits), 2):
            marker = splits[i]
            item_text = splits[i+1].strip()
            if item_text:
                items.append(f"{marker} {item_text}")
        
        # 添加有序列表（修复原逻辑中重复创建段落的问题）
        for item in items:
            list_para = self.doc.add_paragraph(item)
            self._format_body(list_para)
            list_para.paragraph_format.left_indent = Inches(0.5)

    def _add_unordered_list(self, para, content):
        """添加无序列表（适配 AI 返回的 -、· 格式）"""
        logger.debug(f"处理无序列表: {content[:50]}...")
        # 兼容 - 和 · 两种分隔符
        content = content.replace("·", "-")
        items = [item.strip() for item in content.split("-") if item.strip()]
        for item in items:
            list_para = self.doc.add_paragraph(f"- {item}")
            self._format_body(list_para)
            list_para.paragraph_format.left_indent = Inches(0.5)

    def _format_title(self, para):
        """格式化标题：黑体、二号、居中、加粗"""
        para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        for run in para.runs:
            run.font.name = '黑体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
            run.font.size = Pt(22)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 0, 0)  # 黑色

    def _format_body(self, para):
        """格式化正文：宋体、小四、1.5倍行距、段首缩进2字符、两端对齐"""
        # 设置段落格式
        para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        para.paragraph_format.line_spacing = 1.5  # 1.5倍行距
        para.paragraph_format.first_line_indent = Pt(21.0)  # 段首缩进2字符（21磅）
        
        for run in para.runs:
            run.font.name = '宋体'
            run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
            run.font.size = Pt(12)
            run.font.color.rgb = RGBColor(68, 68, 68)  # 深灰色，更护眼

    def _process_tables(self):
        """统一表格样式（保留原有逻辑）"""
        table_count = len(self.doc.tables)
        logger.info(f"处理 {table_count} 个表格")
        for i, table in enumerate(self.doc.tables):
            logger.debug(f"处理第 {i+1} 个表格")
            table.style = 'Table Grid'
            # 设置表格宽度为页面宽度的 90%
            table.autofit = False
            for row in table.rows:
                for cell in row.cells:
                    cell.width = Inches(6.5)  # 适配 A4 纸
                    for para in cell.paragraphs:
                        self._format_body(para)

    def _process_images(self):
        """规范图片对齐：居中对齐，规定长宽（保留原有逻辑）"""
        logger.info("开始处理文档中的图片")
        
        # 计数处理的图片数量
        image_count = 0
        
        # 遍历所有段落，查找包含图片的段落
        for paragraph in self.doc.paragraphs:
            # 检查段落是否包含图片
            if '<pic:pic' in paragraph._element.xml or 'a:pic' in paragraph._element.xml:
                # 设置图片居中对齐
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                # 设置图片段落的格式
                paragraph.paragraph_format.space_after = Pt(12)  # 段后间距
                paragraph.paragraph_format.space_before = Pt(12)  # 段前间距
                
                image_count += 1
        
        logger.info(f"共检测并处理了 {image_count} 张图片，已设置居中对齐")