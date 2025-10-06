#!/usr/bin/env python
"""
测试水印旋转功能
"""

import os
import sys
from PIL import Image

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from watermark_processor import WatermarkProcessor, WatermarkPosition

def test_rotation():
    """测试旋转功能"""
    # 创建一个简单的测试图片
    test_image = Image.new('RGB', (400, 300), color='white')
    test_image_path = os.path.join(current_dir, 'test_image.jpg')
    test_image.save(test_image_path, 'JPEG')
    
    # 创建水印处理器
    processor = WatermarkProcessor()
    
    # 测试不同的旋转角度
    rotation_angles = [0, 45, 90, 135, 180, -45, -90, -135]
    
    for angle in rotation_angles:
        try:
            print(f"测试旋转角度: {angle}度")
            
            # 添加旋转水印
            result_image = processor.add_watermark(
                image_path=test_image_path,
                date_text="2025:01:01",
                font_size=36,
                color="#FF0000",
                position=WatermarkPosition.CENTER,
                opacity=0.8,
                rotation=angle
            )
            
            # 保存结果 - 转换为RGB模式以兼容JPEG格式
            if result_image.mode == 'RGBA':
                # 创建白色背景
                background = Image.new('RGB', result_image.size, (255, 255, 255))
                background.paste(result_image, mask=result_image.split()[3])  # 使用alpha通道作为遮罩
                result_image = background
            
            # 保存结果
            output_path = os.path.join(current_dir, f'test_rotation_{angle}.jpg')
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
    test_rotation()