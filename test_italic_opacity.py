#!/usr/bin/env python
"""
测试斜体和透明度功能
"""

import os
import sys
from PIL import Image, ImageDraw

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from src.watermark_processor import WatermarkProcessor, WatermarkPosition


def test_italic_and_opacity():
    """测试斜体和透明度功能"""
    print("=== 测试斜体和透明度功能 ===")
    
    # 创建测试图片
    test_image = Image.new('RGB', (600, 400), color='lightblue')
    draw = ImageDraw.Draw(test_image)
    draw.rectangle([50, 50, 550, 350], outline="white", width=3)
    test_image_path = os.path.join(current_dir, 'test_italic_opacity.jpg')
    test_image.save(test_image_path, 'JPEG')
    
    # 创建水印处理器
    processor = WatermarkProcessor()
    
    # 测试不同的字体样式和透明度组合
    test_cases = [
        {
            "name": "普通文本-不透明",
            "font_style": {"bold": False, "italic": False},
            "opacity": 1.0,
            "color": "#FF0000"
        },
        {
            "name": "斜体文本-半透明",
            "font_style": {"bold": False, "italic": True},
            "opacity": 0.5,
            "color": "#00FF00"
        },
        {
            "name": "粗体文本-半透明",
            "font_style": {"bold": True, "italic": False},
            "opacity": 0.5,
            "color": "#0000FF"
        },
        {
            "name": "粗体斜体-透明",
            "font_style": {"bold": True, "italic": True},
            "opacity": 0.3,
            "color": "#FF00FF"
        }
    ]
    
    for i, case in enumerate(test_cases):
        try:
            print(f"\n测试 {case['name']}:")
            print(f"  字体样式: bold={case['font_style']['bold']}, italic={case['font_style']['italic']}")
            print(f"  透明度: {case['opacity']}")
            print(f"  颜色: {case['color']}")
            
            # 添加水印
            result_image = processor.add_watermark(
                image_path=test_image_path,
                date_text="2025:01:01",
                custom_text=case['name'],
                font_size=36,
                color=case['color'],
                position=WatermarkPosition.CENTER,
                font_style=case['font_style'],
                opacity=case['opacity']
            )
            
            # 保存结果
            output_path = os.path.join(current_dir, f'test_italic_opacity_{i+1}.jpg')
            if result_image.mode == 'RGBA':
                # 转换为RGB模式以兼容JPEG格式
                background = Image.new('RGB', result_image.size, (255, 255, 255))
                background.paste(result_image, mask=result_image.split()[3])  # 使用alpha通道作为遮罩
                result_image = background
            result_image.save(output_path, 'JPEG')
            print(f"  ✓ 成功保存到: {output_path}")
            
        except Exception as e:
            print(f"  ❌ 失败: {e}")
    
    # 清理测试图片
    try:
        os.remove(test_image_path)
    except:
        pass
    
    print("\n测试完成！")


if __name__ == "__main__":
    test_italic_and_opacity()