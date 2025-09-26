#!/usr/bin/env python
"""
导出功能测试脚本
测试新增的导出设置：输出目录、命名规则、JPEG质量、图片尺寸调整等
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_export_test_images():
    """创建用于测试导出功能的图片"""
    # 创建测试目录
    test_dir = "test_export"
    os.makedirs(test_dir, exist_ok=True)
    
    # 定义要创建的测试图片
    images_info = [
        # (文件名, 尺寸, 颜色, EXIF日期, 描述)
        ("large_photo.jpg", (2000, 1500), "red", "2024:01:15 10:30:00", "大尺寸JPEG图片"),
        ("medium_photo.png", (1200, 800), "blue", None, "中等尺寸PNG图片"),
        ("small_photo.jpg", (800, 600), "green", "2024:02:20 14:15:30", "小尺寸JPEG图片"),
        ("square_photo.png", (1000, 1000), "yellow", None, "正方形PNG图片"),
    ]
    
    for filename, size, color, exif_date, description in images_info:
        try:
            print(f"正在创建: {filename} - {description}")
            
            # 创建图像
            img = Image.new('RGB', size, color)
            draw = ImageDraw.Draw(img)
            
            # 添加装饰性内容
            draw.rectangle([20, 20, size[0]-20, size[1]-20], outline="white", width=5)
            
            # 添加文本信息
            draw.text((50, 50), f"测试图片: {filename}", fill="white")
            draw.text((50, 100), f"尺寸: {size[0]}x{size[1]}", fill="white")
            draw.text((50, 150), f"颜色: {color}", fill="white")
            draw.text((50, 200), description, fill="white")
            
            # 添加网格线帮助观察缩放效果
            for i in range(0, size[0], 100):
                draw.line([(i, 0), (i, size[1])], fill="white", width=1)
            for i in range(0, size[1], 100):
                draw.line([(0, i), (size[0], i)], fill="white", width=1)
            
            filepath = os.path.join(test_dir, filename)
            
            # 保存图片，根据格式处理EXIF
            if filename.endswith('.jpg') and exif_date:
                # 为JPEG添加EXIF信息
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
                img.save(filepath, "JPEG", exif=exif_bytes, quality=95)
            else:
                img.save(filepath)
            
            print(f"  ✅ 成功创建: {filepath}")
            
        except Exception as e:
            print(f"  ❌ 创建失败 {filename}: {e}")
    
    print(f"\n测试图片已保存到目录: {os.path.abspath(test_dir)}")
    return test_dir

def test_export_features():
    """测试导出功能"""
    print("=== 导出功能测试 ===")
    
    # 创建测试图片
    test_dir = create_export_test_images()
    
    # 创建不同的输出目录用于测试
    output_dirs = [
        "output_original",
        "output_prefix", 
        "output_suffix",
        "output_resize"
    ]
    
    for output_dir in output_dirs:
        os.makedirs(output_dir, exist_ok=True)
    
    print("\n测试场景:")
    print("1. GUI界面测试:")
    print("   - 运行 'python gui_app.py' 启动GUI应用")
    print(f"   - 导入 {test_dir} 文件夹中的测试图片")
    print("   - 测试以下功能组合:")
    
    print("\n2. 输出目录测试:")
    print("   - 选择不同的输出目录")
    print("   - 验证不能选择原文件夹作为输出目录")
    
    print("\n3. 命名规则测试:")
    print("   - original: 保持原文件名")
    print("   - prefix: 添加前缀 'wm_'")
    print("   - suffix: 添加后缀 '_watermarked'")
    print("   - 自定义前缀/后缀")
    
    print("\n4. JPEG质量测试:")
    print("   - 设置不同的质量值 (30, 60, 95)")
    print("   - 观察文件大小和图片质量变化")
    
    print("\n5. 图片尺寸调整测试:")
    print("   - none: 保持原尺寸")
    print("   - width: 按宽度缩放 (设置800px)")
    print("   - height: 按高度缩放 (设置600px)")
    print("   - percent: 按百分比缩放 (设置0.5倍)")
    
    print("\n6. 综合测试场景:")
    test_scenarios = [
        {
            "name": "场景1: 保持原名 + PNG输出",
            "settings": {
                "命名规则": "original",
                "输出格式": "png",
                "尺寸调整": "none"
            }
        },
        {
            "name": "场景2: 前缀命名 + JPEG高质量",
            "settings": {
                "命名规则": "prefix (wm_)",
                "输出格式": "jpeg",
                "JPEG质量": "95",
                "尺寸调整": "none"
            }
        },
        {
            "name": "场景3: 后缀命名 + 按宽度缩放",
            "settings": {
                "命名规则": "suffix (_processed)",
                "输出格式": "auto",
                "尺寸调整": "width (800px)"
            }
        },
        {
            "name": "场景4: 综合测试",
            "settings": {
                "命名规则": "prefix (thumb_)",
                "输出格式": "jpeg",
                "JPEG质量": "75",
                "尺寸调整": "percent (0.3)"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n   {scenario['name']}:")
        for key, value in scenario['settings'].items():
            print(f"     - {key}: {value}")
    
    print("\n预期结果:")
    print("✅ 不能选择原文件夹作为输出目录")
    print("✅ 不同命名规则生成正确的文件名")
    print("✅ JPEG质量调节影响文件大小")
    print("✅ 图片尺寸调整功能正常")
    print("✅ 各种设置组合都能正常工作")
    print("✅ 输出目录中生成正确的文件")
    
    return test_dir

def main():
    """主函数"""
    test_dir = test_export_features()
    
    print(f"\n📁 测试文件位置: {os.path.abspath(test_dir)}")
    print(f"🎯 输出目录已创建: output_*")
    print("\n🔧 测试重点:")
    print("1. 输出目录验证（防止覆盖原图）")
    print("2. 文件命名规则正确性")
    print("3. JPEG质量对文件大小的影响")
    print("4. 图片尺寸调整准确性")
    print("5. 各种设置组合的兼容性")
    
    print("\n💡 使用提示:")
    print("- 可以用文件管理器查看不同输出目录的结果")
    print("- 比较不同JPEG质量设置的文件大小")
    print("- 检查缩放后的图片尺寸是否正确")

if __name__ == "__main__":
    main()