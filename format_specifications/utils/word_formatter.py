from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import parse_xml
from docx.oxml.shared import OxmlElement
import os
import logging
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
        """处理所有段落：AI 优化 + 样式设置"""
        logger.info("开始处理所有段落")

        # 先收集所有原始段落文本（避免边遍历边修改导致索引混乱）
        raw_paragraphs = [para.text for para in self.doc.paragraphs]
        total_paragraphs = len(raw_paragraphs)
        logger.info(f"检测到 {total_paragraphs} 个段落")

        # 合并所有原始文本（处理跨段落的大段文字）
        merged_raw_text = "\n".join([text for text in raw_paragraphs if text.strip()])
        logger.info(f"合并原始文本，总长度: {len(merged_raw_text)} 字符")

        # 检查是否有原始内容
        if not merged_raw_text.strip():
            logger.warning("原始文档中没有文本内容，保留原始文档结构")
            return

        # AI 处理文本（润色、分段、分点）
        processed_text = None
        if self.use_ai:
            logger.info("开始AI文本处理...")
            try:
                ai_processed_text = self.ai_processor.process_text(merged_raw_text)
                logger.info("AI文本处理完成")

                # 检查AI处理结果是否为空
                if ai_processed_text and ai_processed_text.strip():
                    processed_text = ai_processed_text
                else:
                    logger.warning("AI返回空内容，保留原始文档")
                    return  # 直接返回，不做清空和格式化
            except Exception as e:
                logger.error(f"AI处理出错: {str(e)}，保留原始文档")
                return  # 出错也直接返回，保留原文档
        else:
            logger.info("跳过AI处理，使用原始文本")
            processed_text = merged_raw_text

        # ===== 只有确认 processed_text 有内容才继续 =====
        if not processed_text or not processed_text.strip():
            logger.warning("处理后文本为空，保留原始文档结构")
            return

        # 清空原有段落（保留文档结构，只删除文本）
        for para in self.doc.paragraphs:
            para.clear()

        # 将处理后的文本拆分为段落（空行分隔），重新添加到文档
        processed_paragraphs = [p.strip() for p in processed_text.split("\n\n") if p.strip()]
        logger.info(f"处理后段落数: {len(processed_paragraphs)}")

        # 如果没有处理后的段落，至少添加一个空段落以保留文档结构
        if not processed_paragraphs:
            logger.warning("没有处理后的段落内容，添加一个空段落")
            self.doc.add_paragraph("")
        else:
            for para_content in processed_paragraphs:
                new_para = self.doc.add_paragraph()
                # 处理分点内容（有序列表/无序列表）
                if para_content.startswith(("1.", "2.", "3.")):
                    self._add_ordered_list(new_para, para_content)
                elif para_content.startswith(("-", "·")):
                    self._add_unordered_list(new_para, para_content)
                else:
                    # 普通段落（标题/正文）
                    new_para.text = para_content
                    if para_content.startswith(("第", "一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、")):
                        self._format_title(new_para)
                    else:
                        self._format_body(new_para)
    def _add_ordered_list(self, para, content):
        """添加有序列表（适配 AI 返回的 1.、2. 格式）"""
        logger.debug(f"处理有序列表: {content[:50]}...")
        # 拆分列表项（按 数字. 拆分）
        items = []
        import re
        # 正则匹配 1.、2. 等标记，拆分列表项
        splits = re.split(r'(\d+\.)', content)
        for i in range(1, len(splits), 2):
            marker = splits[i]
            item_text = splits[i+1].strip()
            if item_text:
                items.append(f"{marker} {item_text}")
        
        # 添加有序列表
        for item in items:
            list_para = self.doc.add_paragraph(item)
            self._format_body(list_para)
            # 设置列表缩进（优化显示）
            list_para.paragraph_format.left_indent = Inches(0.5)

    def _add_unordered_list(self, para, content):
        """添加无序列表（适配 AI 返回的 -、· 格式）"""
        logger.debug(f"处理无序列表: {content[:50]}...")
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
        """统一表格样式"""
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
        """规范图片对齐：居中对齐，规定长宽"""
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
        
        # 注意：由于python-docx对图片尺寸的限制，这里仅设置对齐方式
        # 如果需要精确控制图片尺寸，可能需要直接操作底层XML或使用其他库