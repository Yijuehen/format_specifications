from django.shortcuts import render
from django.http import FileResponse, HttpResponseBadRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from .utils import generate_output_path
from .utils.word_formatter import AIWordFormatter
import os
from datetime import datetime
from django.conf import settings
import logging

# 获取logger实例
logger = logging.getLogger(__name__)

# 上传页面（新增 AI 开关选项）
def upload_word_page(request):
    logger.info("访问上传页面")
    return render(request, 'upload_word_ai.html')

# 处理 AI 辅助格式化
@require_http_methods(["POST"])
def ai_format_word(request):
    logger.info("开始处理AI格式化请求")
    
    # 1. 检查文件上传
    if 'word_file' not in request.FILES:
        error_msg = "请上传 Word 文件"
        logger.warning(error_msg)
        return render(request, 'upload_word_ai.html', {'error': error_msg})
    
    uploaded_file = request.FILES['word_file']
    if not uploaded_file.name.endswith(('.docx',)):
        error_msg = "仅支持 .docx 格式（.doc 需先转换为 .docx）"
        logger.warning(error_msg)
        return render(request, 'upload_word_ai.html', {'error': error_msg})
    
    # 2. 检查是否启用 AI
    use_ai = request.POST.get('use_ai', 'on') == 'on'  # 前端传的开关状态
    logger.info(f"AI功能启用状态: {use_ai}")
    
    # 3. 保存上传文件
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploaded_words')
    os.makedirs(upload_dir, exist_ok=True)
    input_file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(input_file_path, 'wb') as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    
    # 4. 生成输出文件路径
    output_file_path, output_filename = generate_output_path(uploaded_file)
    print(output_filename)
    
    # 5. 执行 AI 格式化
    try:
        logger.info(f"开始格式化文件: {input_file_path}, 输出到: {output_file_path}")
        formatter = AIWordFormatter(input_file_path, use_ai=use_ai)
        result = formatter.format(output_file_path)
        logger.info("文件格式化完成")
        
        # 检查生成的文件是否为空
        if os.path.getsize(output_file_path) == 0:
            os.remove(output_file_path)
            raise ValueError("生成的文件为空，请重试")
        
        # 记录原始文件名和生成的文件名
        logger.info(f"原始文件名: {uploaded_file.name}, 生成文件名: {output_filename}")
        
        # 返回文件下载，设置正确的Content-Disposition头
        response = FileResponse(open(output_file_path, 'rb'))
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        # 使用引号包围文件名，确保浏览器正确处理包含中文的文件名

        from urllib.parse import quote  # 导入URL编码模块
        # 1. 对文件名做URL编码（解决中文/特殊字符）
        encoded_filename = quote(output_filename)
        response['Content-Disposition'] = (
            f'attachment; filename="{encoded_filename}"; '
            f'filename*=UTF-8\'\'{encoded_filename}'
        )
        
        return response
        
    except ValueError as ve:
        # AI返回空或文件为空的情况
        return render(request, 'upload_word_ai.html', {'error': str(ve)})
    except Exception as e:
        # 其他错误
        return render(request, 'upload_word_ai.html', {'error': f"处理失败：{str(e)}"})