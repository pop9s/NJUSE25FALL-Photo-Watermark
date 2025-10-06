#!/usr/bin/env python
"""
图片水印功能测试脚本
测试新增的图片水印功能，包括透明PNG支持、缩放和透明度调节
"""

import os
import sys
from PIL import Image, ImageDraw
from datetime import datetime
import piexif

def create_test_images():
    """创建测试图片"""
    # 创建测试目录
    test_dir = "test_image_watermark"
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建背景测试图片
    background_img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(background_img)
    
    # 添加一些装饰
    draw.rectangle([50, 50, 750, 550], outline="blue", width=3)
    draw.ellipse([200, 150, 600, 450], outline="red", width=2)
    
    # 添加EXIF信息
    exif_dict = {
        "0th": {},
        "Exif": {
            piexif.ExifIFD.DateTimeOriginal: "2024:03:15 10:30:00",
        },
        "GPS": {},
        "1st": {},
        "thumbnail": None
    }
    exif_bytes = piexif.dump(exif_dict)
    
    # 保存背景图片
    background_path = os.path.join(test_dir, "background.jpg")
    background_img.save(background_path, "JPEG", exif=exif_bytes)
    
    # 创建带透明背景的PNG水印图片 (Logo样式)
    watermark_img = Image.new('RGBA', (200, 100), (0, 0, 0, 0))  # 完全透明背景
    watermark_draw = ImageDraw.Draw(watermark_img)
    
    # 绘制一个简单的Logo样式图形
    watermark_draw.ellipse([10, 10, 190, 90], fill=(255, 0, 0, 128), outline=(0, 0, 0, 255), width=2)
    watermark_draw.text((70, 40), "LOGO", fill=(255, 255, 255, 255))
    
    # 保存水印图片
    watermark_path = os.path.join(test_dir, "logo.png")
    watermark_img.save(watermark_path, "PNG")
    
    print(f"✅ 背景图片已创建: {background_path}")
    print(f"✅ 水印图片已创建: {watermark_path}")
    return test_dir, background_path, watermark_path

def test_command_line_features():
    """测试命令行功能"""
    print("=== 命令行功能测试 ===")
    
    test_dir, background_path, watermark_path = create_test_images()
    
    # 测试用例
    test_cases = [
        {
            "name": "1. 基本图片水印",
            "cmd": f'python main.py "{background_path}" --image-watermark "{watermark_path}" --output-dir "{test_dir}/output1"'
        },
        {
            "name": "2. 图片水印+缩放",
            "cmd": f'python main.py "{background_path}" --image-watermark "{watermark_path}" --image-watermark-scale 0.5 --output-dir "{test_dir}/output2"'
        },
        {
            "name": "3. 图片水印+透明度",
            "cmd": f'python main.py "{background_path}" --image-watermark "{watermark_path}" --opacity 0.5 --output-dir "{test_dir}/output3"'
        },
        {
            "name": "4. 图片水印+缩放+透明度",
            "cmd": f'python main.py "{background_path}" --image-watermark "{watermark_path}" --image-watermark-scale 0.7 --opacity 0.7 --output-dir "{test_dir}/output4"'
        },
        {
            "name": "5. 图片水印+位置调整",
            "cmd": f'python main.py "{background_path}" --image-watermark "{watermark_path}" --position "top_left" --output-dir "{test_dir}/output5"'
        },
        {
            "name": "6. 保持原有功能：文本水印",
            "cmd": f'python main.py "{background_path}" --custom-text "文本水印" --font-size 48 --color "#FF0000" --output-dir "{test_dir}/output6"'
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}")
        print(f"   命令: {test_case['cmd']}")
        
        try:
            result = os.system(test_case['cmd'])
            if result == 0:
                print("   ✅ 执行成功")
            else:
                print("   ❌ 执行失败")
        except Exception as e:
            print(f"   ❌ 执行错误: {e}")
    
    print(f"\n📁 测试结果保存在: {os.path.abspath(test_dir)}")

def test_gui_features():
    """测试GUI功能说明"""
    print("\n=== GUI功能测试说明 ===")
    print("1. 运行 'python gui_app.py' 启动GUI应用")
    print("2. 导入背景测试图片")
    print("3. 在'图片水印设置'区域测试以下功能:")
    print("   - 点击'浏览'按钮选择水印图片")
    print("   - 调整'缩放比例'数值")
    print("4. 调整透明度滑块来控制水印透明度")
    print("5. 点击'开始处理'并检查输出图片效果")

def main():
    """主函数"""
    print("🖼️  图片水印功能测试")
    print("=" * 50)
    
    # 测试命令行功能
    test_command_line_features()
    
    # 测试GUI功能说明
    test_gui_features()
    
    print("\n🎉 测试完成！")
    print("请检查输出目录中的图片，验证图片水印功能是否正常工作。")

if __name__ == "__main__":
    main()