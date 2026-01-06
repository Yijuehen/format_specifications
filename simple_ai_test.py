"""
简单AI文本处理功能测试
"""
import os
import sys
import django

# 添加项目路径
sys.path.append('.')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'format_specifications.settings')
django.setup()

from format_specifications.utils.ai_word_utils import AITextProcessor

def main():
    print("开始测试AI文本处理功能...")
    
    # 创建AI文本处理器
    try:
        processor = AITextProcessor()
        print("✅ AI文本处理器创建成功")
    except Exception as e:
        print(f"❌ 创建AI文本处理器失败: {e}")
        print("请检查settings.py中的ZHIPU_API_KEY和ZHIPU_MODEL配置")
        return
    
    # 测试文本
    test_text = """
    人工智能是计算机科学的一个分支它致力于让机器具备类似人类的智能行为如学习推理规划和自然交互人工智能技术正在快速发展并广泛应用于各个领域包括医疗保健金融服务交通运输和教育等这些应用正在改变我们的生活方式和工作模式
    """
    
    print(f"\n原始文本：\n{test_text.strip()}")
    
    try:
        print("\n正在调用AI处理...")
        processed_text = processor.process_text(test_text.strip())
        
        print(f"\nAI处理后文本：\n{processed_text}")
        
        # 验证结果
        if processed_text and processed_text.strip():
            print("\n✅ 测试成功：AI返回了有效内容")
            
            # 检查分段情况
            paragraphs = [p for p in processed_text.split('\n\n') if p.strip()]
            print(f"段落数量: {len(paragraphs)}")
            
            # 检查是否有列表项
            lines = processed_text.split('\n')
            list_items = [line for line in lines if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '-', '·'))]
            if list_items:
                print(f"列表项数量: {len(list_items)}")
                for item in list_items[:3]:  # 显示前3个列表项
                    print(f"  - {item[:50]}...")
            
        else:
            print("\n❌ 测试失败：AI返回了空内容")
            
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")

if __name__ == "__main__":
    main()