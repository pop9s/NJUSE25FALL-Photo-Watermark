#!/usr/bin/env python
"""
测试字体选择功能与现有功能的兼容性
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from watermark_processor import WatermarkProcessor, WatermarkPosition

def test_font_compatibility():
    """测试字体兼容性"""
    # 创建一个简单的测试图片
    test_image = Image.new('RGB', (400, 300), color='white')
    test_image_path = os.path.join(current_dir, 'test_font_image.jpg')
    test_image.save(test_image_path, 'JPEG')
    
    # 创建水印处理器
    processor = WatermarkProcessor()
    
    # 测试不同的字体和样式组合
    print("测试默认字体")
    try:
        result_image = processor.add_watermark(
            image_path=test_image_path,
            date_text="2025:01:01",
            font_size=36,
            color="#FF0000",
            position=WatermarkPosition.CENTER
        )
        
        output_path = os.path.join(current_dir, "test_font_default.jpg")
        if result_image.mode == 'RGBA':
            background = Image.new('RGB', result_image.size, (255, 255, 255))
            background.paste(result_image, mask=result_image.split()[3])
            result_image = background
        result_image.save(output_path, 'JPEG')
        print(f"  ✓ 成功保存到: {output_path}")
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    print("测试字体样式")
    try:
        result_image = processor.add_watermark(
            image_path=test_image_path,
            date_text="粗体测试",
            font_size=36,
            color="#00FF00",
            position=WatermarkPosition.TOP_LEFT,
            font_style={'bold': True, 'italic': False}
        )
        
        output_path = os.path.join(current_dir, "test_font_bold.jpg")
        if result_image.mode == 'RGBA':
            background = Image.new('RGB', result_image.size, (255, 255, 255))
            background.paste(result_image, mask=result_image.split()[3])
            result_image = background
        result_image.save(output_path, 'JPEG')
        print(f"  ✓ 成功保存到: {output_path}")
        
    except Exception as e:
        print(f"  ❌ 失败: {e}")
    
    # 测试字体与其他功能的组合
    print("\n测试字体与其他功能的组合:")
    try:
        result_image = processor.add_watermark(
            image_path=test_image_path,
            date_text="组合测试",
            font_size=48,
            color="#0000FF",
            position=WatermarkPosition.BOTTOM_RIGHT,
            font_style={'bold': True, 'italic': False},
            shadow=True,
            stroke=True,
            opacity=0.8,
            rotation=30
        )
        
        # 保存结果
        output_path = os.path.join(current_dir, "test_font_combined.jpg")
        if result_image.mode == 'RGBA':
            background = Image.new('RGB', result_image.size, (255, 255, 255))
            background.paste(result_image, mask=result_image.split()[3])
            result_image = background
        result_image.save(output_path, 'JPEG')
        print(f"  ✓ 组合功能测试成功，保存到: {output_path}")
        
    except Exception as e:
        print(f"  ❌ 组合功能测试失败: {e}")
    
    # 清理测试图片
    try:
        os.remove(test_image_path)
    except:
        pass
    
    print("\n字体兼容性测试完成！")

if __name__ == "__main__":
    test_font_compatibility()