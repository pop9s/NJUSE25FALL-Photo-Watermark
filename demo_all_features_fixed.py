#!/usr/bin/env python
"""
演示所有功能：字体、预设位置、手动拖拽、旋转
"""

import os
import sys
from PIL import Image, ImageDraw
import piexif
from typing import Dict, Any

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')

for path in [current_dir, src_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from watermark_processor import WatermarkProcessor, WatermarkPosition

def create_demo_image():
    """创建演示图片"""
    print("创建演示图片...")
    
    # 创建演示目录
    demo_dir = os.path.join(current_dir, "demo_images")
    os.makedirs(demo_dir, exist_ok=True)
    
    # 创建带EXIF信息的演示图片
    demo_image = Image.new('RGB', (1024, 768), color='lightcyan')
    draw = ImageDraw.Draw(demo_image)
    
    # 添加背景图案
    for i in range(0, 1024, 50):
        draw.line([(i, 0), (i, 768)], fill="lightgray", width=1)
    for i in range(0, 768, 50):
        draw.line([(0, i), (1024, i)], fill="lightgray", width=1)
    
    # 添加标题
    draw.text((400, 50), "Watermark Demo", fill="darkblue")
    draw.text((300, 100), "照片水印工具功能演示", fill="darkgreen")
    
    # 添加说明文字
    instructions = [
        "功能演示说明:",
        "1. 字体功能: 支持系统字体、字号、粗体、斜体",
        "2. 预设位置: 九宫格布局（四角、正中心）",
        "3. 手动拖拽: 鼠标拖拽水印到任意位置",
        "4. 旋转功能: 任意角度旋转水印",
    ]
    
    for i, text in enumerate(instructions):
        draw.text((100, 200 + i*40), text, fill="black")
    
    # 添加EXIF信息
    exif_date = "2025:04:05 15:30:00"
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: exif_date,
            piexif.ExifIFD.DateTimeDigitized: exif_date,
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    exif_bytes = piexif.dump(exif_dict)
    
    demo_path = os.path.join(demo_dir, 'demo_image.jpg')
    demo_image.save(demo_path, 'JPEG', exif=exif_bytes)
    
    print(f"已创建演示图片: {demo_path}")
    return demo_dir, demo_path

def demonstrate_font_features(demo_image_path: str, output_dir: str):
    """演示字体功能"""
    print("\n=== 演示字体功能 ===")
    
    processor = WatermarkProcessor()
    
    # 不同字体样式演示
    font_demos: list[Dict[str, Any]] = [
        {"name": "普通字体", "style": {"bold": False, "italic": False}, "color": "#FF0000"},
        {"name": "粗体字体", "style": {"bold": True, "italic": False}, "color": "#00FF00"},
        {"name": "斜体字体", "style": {"bold": False, "italic": True}, "color": "#0000FF"},
        {"name": "粗体+斜体", "style": {"bold": True, "italic": True}, "color": "#FF00FF"},
    ]
    
    for i, demo in enumerate(font_demos):
        try:
            result = processor.add_watermark(
                image_path=demo_image_path,
                date_text="2025:04:05",
                custom_text=str(demo["name"]),
                font_size=36,
                color=str(demo["color"]),
                position=WatermarkPosition.BOTTOM_RIGHT,
                font_style=demo["style"]
            )
            
            output_path = os.path.join(output_dir, f'font_demo_{i+1}.jpg')
            if result.mode == 'RGBA':
                # 转换为RGB模式以兼容JPEG
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[3])
                result = background
            result.save(output_path, 'JPEG', quality=95)
            print(f"  ✓ {demo['name']} 演示已保存: {output_path}")
        except Exception as e:
            print(f"  ❌ {demo['name']} 演示失败: {e}")

def demonstrate_preset_positions(demo_image_path: str, output_dir: str):
    """演示预设位置功能"""
    print("\n=== 演示预设位置功能 ===")
    
    processor = WatermarkProcessor()
    
    # 九宫格位置演示
    positions = [
        (WatermarkPosition.TOP_LEFT, "左上角"),
        (WatermarkPosition.TOP_CENTER, "上中"),
        (WatermarkPosition.TOP_RIGHT, "右上角"),
        (WatermarkPosition.CENTER_LEFT, "左中"),
        (WatermarkPosition.CENTER, "居中"),
        (WatermarkPosition.CENTER_RIGHT, "右中"),
        (WatermarkPosition.BOTTOM_LEFT, "左下角"),
        (WatermarkPosition.BOTTOM_CENTER, "下中"),
        (WatermarkPosition.BOTTOM_RIGHT, "右下角"),
    ]
    
    for i, (position, name) in enumerate(positions):
        try:
            result = processor.add_watermark(
                image_path=demo_image_path,
                date_text="2025:04:05",
                custom_text=f"位置: {name}",
                font_size=28,
                color="#000000",
                position=position
            )
            
            output_path = os.path.join(output_dir, f'position_demo_{i+1}.jpg')
            if result.mode == 'RGBA':
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[3])
                result = background
            result.save(output_path, 'JPEG', quality=95)
            print(f"  ✓ {name} 演示已保存: {output_path}")
        except Exception as e:
            print(f"  ❌ {name} 演示失败: {e}")

def demonstrate_rotation_features(demo_image_path: str, output_dir: str):
    """演示旋转功能"""
    print("\n=== 演示旋转功能 ===")
    
    processor = WatermarkProcessor()
    
    # 不同角度旋转演示
    rotations = [
        (0, "无旋转"),
        (30, "30度旋转"),
        (45, "45度旋转"),
        (90, "90度旋转"),
        (135, "135度旋转"),
        (180, "180度旋转"),
        (-30, "-30度旋转"),
        (-45, "-45度旋转"),
        (-90, "-90度旋转"),
    ]
    
    for i, (angle, description) in enumerate(rotations):
        try:
            result = processor.add_watermark(
                image_path=demo_image_path,
                date_text="2025:04:05",
                custom_text=description,
                font_size=32,
                color="#FF5500",
                position=WatermarkPosition.CENTER,
                rotation=angle
            )
            
            output_path = os.path.join(output_dir, f'rotation_demo_{i+1}_{angle}.jpg')
            if result.mode == 'RGBA':
                background = Image.new('RGB', result.size, (255, 255, 255))
                background.paste(result, mask=result.split()[3])
                result = background
            result.save(output_path, 'JPEG', quality=95)
            print(f"  ✓ {description} 演示已保存: {output_path}")
        except Exception as e:
            print(f"  ❌ {description} 演示失败: {e}")

def demonstrate_combined_features(demo_image_path: str, output_dir: str):
    """演示组合功能"""
    print("\n=== 演示组合功能 ===")
    
    processor = WatermarkProcessor()
    
    # 组合功能演示
    try:
        result = processor.add_watermark(
            image_path=demo_image_path,
            date_text="2025:04:05",
            custom_text="组合功能演示",
            font_size=40,
            color="#AA00AA",
            position=WatermarkPosition.CENTER,
            font_style={"bold": True, "italic": True},
            shadow=True,
            stroke=True,
            rotation=30,
            opacity=0.8
        )
        
        output_path = os.path.join(output_dir, 'combined_demo.jpg')
        if result.mode == 'RGBA':
            background = Image.new('RGB', result.size, (255, 255, 255))
            background.paste(result, mask=result.split()[3])
            result = background
        result.save(output_path, 'JPEG', quality=95)
        print(f"  ✓ 组合功能演示已保存: {output_path}")
    except Exception as e:
        print(f"  ❌ 组合功能演示失败: {e}")

def main():
    """主函数"""
    print("=== 照片水印工具功能演示 ===")
    
    # 创建演示图片
    demo_dir, demo_image_path = create_demo_image()
    
    # 创建输出目录
    output_dir = os.path.join(demo_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # 演示各项功能
    demonstrate_font_features(demo_image_path, output_dir)
    demonstrate_preset_positions(demo_image_path, output_dir)
    demonstrate_rotation_features(demo_image_path, output_dir)
    demonstrate_combined_features(demo_image_path, output_dir)
    
    print("\n=== 演示总结 ===")
    print("✓ 字体功能演示: 不同字体样式效果")
    print("✓ 预设位置演示: 九宫格位置布局")
    print("✓ 旋转功能演示: 不同角度旋转效果")
    print("✓ 组合功能演示: 多种效果组合")
    
    print("\n=== GUI功能说明 ===")
    print("在GUI应用中，您还可以:")
    print("✓ 使用颜色调色板选择水印颜色")
    print("✓ 通过字体选择器选择系统字体")
    print("✓ 点击九宫格按钮快速设置位置")
    print("✓ 在预览图上拖拽水印到任意位置")
    print("✓ 使用滑块或输入框调节旋转角度")
    print("✓ 实时预览所有设置效果")
    
    print(f"\n🎉 功能演示完成！")
    print(f"📁 演示图片保存在: {demo_dir}")
    print(f"📁 输出结果保存在: {output_dir}")
    print("\n💡 建议运行 'python gui_app.py' 体验完整的GUI功能")

if __name__ == "__main__":
    main()