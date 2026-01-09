import os
from django.conf import settings

def generate_output_path(uploaded_file, subdir='ai_formatted_words'):
    """生成输出文件路径，文件名带'(改)'后缀"""
    output_dir = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(output_dir, exist_ok=True)

    base_name, ext = os.path.splitext(uploaded_file.name)
    output_filename = f"{base_name}(改){ext}"
    return os.path.join(output_dir, output_filename), output_filename
