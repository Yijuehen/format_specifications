from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.oxml.ns import qn
import logging
import os
import zipfile
import shutil
from pathlib import Path

# 导入 AI 处理类
from .ai_word_utils import AITextProcessor

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AIWordFormatter:
    def __init__(self, input_file_path, use_ai=True):
        """初始化 Word 格式化器，创建可控临时目录（避免权限问题）"""
        self.input_file = input_file_path
        self.doc = Document(input_file_path)
        self.use_ai = use_ai
        self.ai_processor = AITextProcessor() if use_ai else None
        
        # 统一图片尺寸
        self.image_width = Inches(5.91)
        self.image_height = Inches(4.43)
        
        # 可控临时目录（创建在输入文件同目录下，避免系统权限问题）
        self.temp_dir = Path(os.path.dirname(input_file_path)) / "docx_temp_images"
        self.temp_dir.mkdir(exist_ok=True, mode=0o777)  # 赋予最高权限
        
        logger.info(f"AIWordFormatter 初始化完成，文件: {input_file_path}, AI 启用: {use_ai}")
        logger.info(f"临时目录已创建：{self.temp_dir}")

    def __del__(self):
        """析构函数：自动清理临时目录（程序结束时执行）"""
        if self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"临时目录已自动清理：{self.temp_dir}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}，可手动删除：{self.temp_dir}")

    def _ensure_dir_writable(self, dir_path):
        """确保目录存在且可写（解决输出权限问题）"""
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True, mode=0o777)
        if not os.access(dir_path, os.W_OK):
            raise PermissionError(f"无写入权限：{dir_path}")
        return dir_path

    def _extract_images_from_docx(self):
        """从 docx 提取图片（手动写入，无权限问题，提升性能）"""
        image_paths = []
        try:
            with zipfile.ZipFile(self.input_file, 'r') as zip_file:
                # 遍历所有 media 文件夹下的图片
                for file_name in zip_file.namelist():
                    if file_name.startswith('word/media/') and not file_name.endswith('/'):
                        # 简化文件名：避免嵌套路径，提升读取速度
                        img_suffix = file_name.split('.')[-1]
                        img_filename = f"img_{len(image_paths)}.{img_suffix}"
                        img_path = self.temp_dir / img_filename
                        
                        # 手动写入文件（替代 zip.extract，避免权限问题，提升性能）
                        with open(img_path, 'wb') as f:
                            f.write(zip_file.read(file_name))
                        
                        image_paths.append(str(img_path))
                        logger.debug(f"提取图片: {file_name} -> {img_path}")

            logger.info(f"共提取到 {len(image_paths)} 张图片")
            return image_paths

        except Exception as e:
            logger.error(f"提取图片失败: {str(e)}")
            return []

    def _set_text_paragraph_style(self, para):
        """设置文本段落样式（标题/正文区分）"""
        para_text = para.text
        if para_text.startswith(("第", "一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、")):
            # 标题样式
            para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            for run in para.runs:
                run.font.name = '黑体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '黑体')
                run.font.size = Pt(22)
                run.font.bold = True
                run.font.color.rgb = RGBColor(0, 0, 0)
        else:
            # 正文样式
            para.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
            para.paragraph_format.line_spacing = 1.5
            para.paragraph_format.first_line_indent = Pt(21.0)
            
            for run in para.runs:
                run.font.name = '宋体'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), '宋体')
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(68, 68, 68)

    def _process_with_ai(self):
        """启用 AI 时：修复图片丢失 + 无重复日志 + 性能优化"""
        logger.info("启用 AI 处理模式")

        # 1. 提取所有图片（可控临时目录，无权限问题）
        image_paths = self._extract_images_from_docx()
        total_images = len(image_paths)
        
        # 2. 检测所有图片段落和文本段落
        original_paragraphs = list(self.doc.paragraphs)
        image_para_indices = []  # 保存图片段落的原始位置
        pure_texts = []
        text_para_indices = []   # 保存文本段落的原始位置

        for idx, para in enumerate(original_paragraphs):
            para_xml = para._element.xml
            para_text = para.text.strip()
            
            has_image = (
                '<w:drawing>' in para_xml or
                '<pic:pic>' in para_xml or
                '<v:shape' in para_xml or
                '<v:image' in para_xml or
                '<w:pict>' in para_xml
            )
            
            if has_image:
                image_para_indices.append(idx)
                logger.info(f"图片段落 {idx}：文本={para_text[:20]}...")
            elif para_text:
                pure_texts.append(para_text)
                text_para_indices.append(idx)

        logger.info(f"原始文档：{len(image_para_indices)} 个图片段落，{len(pure_texts)} 个纯文本段落")

        # 3. AI 处理文本（无重复日志 + 兜底逻辑）
        processed_text_blocks = []
        if pure_texts:
            merged_text = "\n".join(pure_texts)
            logger.info(f"AI 处理文本长度：{len(merged_text)} 字符")
            try:
                # 调用 AI 处理（AI 内部已打印日志，此处不重复打印）
                processed_text = self.ai_processor.process_text(merged_text)
                
                # 拆分文本块（保留原有逻辑，提升分段准确性）
                if not processed_text or processed_text.strip() == "":
                    logger.error("AI 返回空内容，使用原始文本")
                    processed_text_blocks = pure_texts
                else:
                    logger.info(f"AI 返回原文内容:\n{processed_text}")
                    processed_text_blocks = [p.strip() for p in processed_text.split("\n\n") if p.strip()]
            except Exception as e:
                logger.error(f"AI 处理出错: {str(e)}，使用原始文本")
                processed_text_blocks = pure_texts
        else:
            logger.warning("无纯文本段落")

        logger.info(f"AI 处理后文本块数量：{len(processed_text_blocks)}")

        # 4. 重建文档：按原始段落顺序处理（支持 AI 返回多段落）
        new_doc = Document()
        img_idx = 0
        text_idx = 0
        
        for original_para_idx, para in enumerate(original_paragraphs):
            # 重建图片段落
            if original_para_idx in image_para_indices and img_idx < total_images:
                img_para = new_doc.add_paragraph()
                img_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                img_para.paragraph_format.space_after = Pt(12)
                img_para.paragraph_format.space_before = Pt(12)
                
                try:
                    img_run = img_para.add_run()
                    img_run.add_picture(
                        image_paths[img_idx],
                        width=self.image_width,
                        height=self.image_height
                    )
                    img_idx += 1
                    logger.info(f"插入图片 {img_idx}/{total_images}：{image_paths[img_idx-1]}")
                except Exception as e:
                    logger.warning(f"插入图片 {img_idx} 失败: {e}")
                    img_para.add_run().text = "[图片]"
            
            # 重建文本段落（按顺序插入所有 AI 处理后的段落）
            elif original_para_idx in text_para_indices and text_idx < len(processed_text_blocks):
                text_para = new_doc.add_paragraph(processed_text_blocks[text_idx])
                self._set_text_paragraph_style(text_para)
                text_idx += 1
            else:
                # 空段落或跳过
                new_doc.add_paragraph()

        # 如果 AI 返回了额外的段落（超过原始数量），追加到文档末尾
        while text_idx < len(processed_text_blocks):
            text_para = new_doc.add_paragraph(processed_text_blocks[text_idx])
            self._set_text_paragraph_style(text_para)
            text_idx += 1

        # 替换原文档
        self.doc = new_doc
        logger.info(f"重建完成：{text_idx} 个文本段落 + {img_idx} 个图片段落")

    def _process_without_ai(self):
        """禁用 AI 时：仅统一样式，提升处理速度"""
        logger.info("禁用 AI 处理模式，仅统一样式")
        for para in self.doc.paragraphs:
            self._set_text_paragraph_style(para)

    def _process_all_paragraphs(self):
        """统一处理所有段落（根据 AI 启用状态分支）"""
        logger.info("开始处理所有段落（文本+图片）")
        if self.use_ai:
            self._process_with_ai()
        else:
            self._process_without_ai()

    def _process_tables(self):
        """统一表格样式，提升文档整洁度"""
        table_count = len(self.doc.tables)
        logger.info(f"处理 {table_count} 个表格")
        for i, table in enumerate(self.doc.tables):
            table.style = 'Table Grid'
            table.autofit = False
            for row in table.rows:
                for cell in row.cells:
                    cell.width = Inches(6.5)
                    for para in cell.paragraphs:
                        self._set_text_paragraph_style(para)

    def _process_images(self):
        """规范图片对齐和大小，提升文档美观度"""
        logger.info("开始处理文档中的图片")
        image_count = 0
        for shape in self.doc.inline_shapes:
            try:
                shape.width = self.image_width
                shape.height = self.image_height
                image_count += 1
            except Exception as e:
                logger.warning(f"设置图片大小失败: {str(e)}")

        for paragraph in self.doc.paragraphs:
            para_xml = paragraph._element.xml
            has_image = (
                '<w:drawing>' in para_xml or
                '<pic:pic>' in para_xml or
                'a:pic' in para_xml or
                '<v:shape' in para_xml or
                '<v:image' in para_xml or
                '<w:pict>' in para_xml
            )
            
            if has_image:
                paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                paragraph.paragraph_format.space_after = Pt(12)
                paragraph.paragraph_format.space_before = Pt(12)

        logger.info(f"图片处理完成，共规范化 {image_count} 张图片")

    def format(self, output_file_path):
        """主格式化逻辑：整合所有步骤，确保文件正常输出"""
        output_file_path = Path(output_file_path)
        logger.info(f"开始格式化文件，输入: {self.input_file}，输出: {output_file_path}")
        
        # 确保输出目录可写（解决权限问题）
        try:
            output_dir = self._ensure_dir_writable(output_file_path.parent)
        except PermissionError as e:
            logger.error(f"输出路径权限检查失败: {e}")
            # 降级方案：输出到桌面（确保可写）
            desktop_path = Path(os.path.expanduser("~")) / "Desktop"
            output_file_path = desktop_path / output_file_path.name
            logger.warning(f"降级到桌面输出：{output_file_path}")
            self._ensure_dir_writable(desktop_path)

        # 执行段落、表格、图片处理
        self._process_all_paragraphs()
        logger.info("段落处理完成")
        
        self._process_tables()
        logger.info("表格处理完成")
        
        self._process_images()
        logger.info("图片处理完成")
        
        # 保存文件（兜底重试，避免临时锁定）
        try:
            self.doc.save(str(output_file_path))
            logger.info(f"格式化完成，文件已保存: {output_file_path}")
            return str(output_file_path)
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise